import customtkinter as ctk
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR
import threading

class SiteTrackerSniffer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🌐 Live Web Monitor & Sniffer")
        self.geometry("900x700")
        ctk.set_appearance_mode("Dark")

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="WEB MONITOR", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.start_btn = ctk.CTkButton(self.sidebar, text="▶ START MONITOR", fg_color="green", command=self.toggle_monitor)
        self.start_btn.pack(pady=10, padx=10)

        self.stop_btn = ctk.CTkButton(self.sidebar, text="⏹ STOP", fg_color="red", command=self.stop_monitor)
        self.stop_btn.pack(pady=10, padx=10)

        # --- Main View (Table/List Style) ---
        self.log_box = ctk.CTkTextbox(self, font=("Consolas", 13), text_color="#00FF00")
        self.log_box.pack(expand=True, fill="both", padx=20, pady=20)

        self.is_monitoring = False

    def process_packet(self, pkt):
        if not self.is_monitoring: return

        # DNS Query detect karke website ka naam nikalna
        if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:
            try:
                # Website domain name extract karna
                qname = pkt.getlayer(DNSQR).qname.decode("utf-8")
                # Faltu sites filter karne ke liye (Optional)
                if not any(x in qname for x in ["arpa", "local"]):
                    log_msg = f"[VISITED] Site: {qname[:-1]} | Client: {pkt[IP].src}"
                    self.log_to_gui(log_msg)
            except:
                pass

        # HTTP Host header check (Unencrypted traffic ke liye)
        elif pkt.haslayer(Raw):
            try:
                load = pkt[Raw].load.decode('utf-8', errors='ignore')
                if "Host:" in load:
                    host = load.split("Host: ")[1].split("\r\n")[0]
                    self.log_to_gui(f"[HTTP] Host Found: {host}")
            except:
                pass

    def log_to_gui(self, msg):
        self.log_box.insert("end", f"{msg}\n")
        self.log_box.see("end")

    def run_sniffer(self):
        # UDP port 53 (DNS) filter use kar rahe hain speed ke liye
        sniff(filter="udp port 53 or port 80", prn=self.process_packet, store=0, stop_filter=lambda x: not self.is_monitoring)

    def toggle_monitor(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.log_to_gui("[*] Monitoring started... Tracking web visits.")
            threading.Thread(target=self.run_sniffer, daemon=True).start()

    def stop_monitor(self):
        self.is_monitoring = False
        self.log_to_gui("[!] Monitoring stopped.")

    def clear_logs(self):
        self.log_box.delete("1.0", "end")

if __name__ == "__main__":
    app = SiteTrackerSniffer()
    app.mainloop()
