import customtkinter as ctk
from scapy.all import *
import threading
import socket

class EliteSniffer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ Cyber-Spy Sniffer Pro")
        self.geometry("1000x700")
        ctk.set_appearance_mode("Dark")

        # --- Sidebar Controls ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        self.title_label = ctk.CTkLabel(self.sidebar, text="SNIFFER\nCOMMAND", font=("Orbitron", 20, "bold"))
        self.title_label.pack(pady=20)

        self.start_btn = ctk.CTkButton(self.sidebar, text="▶ START SCAN", fg_color="#27ae60", command=self.toggle_sniffing)
        self.start_btn.pack(pady=10, padx=20)

        self.clear_btn = ctk.CTkButton(self.sidebar, text="🗑 CLEAR LOGS", fg_color="#c0392b", command=self.clear_logs)
        self.clear_btn.pack(pady=10, padx=20)

        # --- Main Console ---
        self.console = ctk.CTkTextbox(self, font=("Consolas", 13), text_color="#00FF00", fg_color="#1a1a1a")
        self.console.pack(expand=True, fill="both", padx=20, pady=20)

        self.is_sniffing = False

    def log(self, text):
        self.console.insert("end", f"{text}\n")
        self.console.see("end")

    def packet_handler(self, pkt):
        if not self.is_sniffing: return
        
        try:
            if pkt.haslayer(IP):
                ip_layer = pkt.getlayer(IP)
                protocol = pkt.summary().split("/")[0] # Basic Proto detect
                
                # Basic Decryption Logic: Yahan hum Raw data ko decode karte hain
                payload = ""
                if pkt.haslayer(Raw):
                    raw_data = pkt[Raw].load
                    try:
                        # Hum bytes ko readable text mein convert karne ki koshish karte hain
                        payload = f" | Data: {raw_data.decode('utf-8', errors='ignore')[:50]}"
                    except:
                        payload = " | Data: [Encrypted/Binary]"

                log_msg = f"[{protocol}] {ip_layer.src} ➔ {ip_layer.dst}{payload}"
                self.log(log_msg)
        except Exception as e:
            pass

    def start_sniff_thread(self):
        sniff(prn=self.packet_handler, store=0, stop_filter=lambda x: not self.is_sniffing)

    def toggle_sniffing(self):
        if not self.is_sniffing:
            self.is_sniffing = True
            self.start_btn.configure(text="⏹ STOP SCAN", fg_color="#e67e22")
            self.log("[*] Initializing Network Tap... Capture Started.")
            threading.Thread(target=self.start_sniff_thread, daemon=True).start()
        else:
            self.is_sniffing = False
            self.start_btn.configure(text="▶ START SCAN", fg_color="#27ae60")
            self.log("[!] Scan Interrupted.")

    def clear_logs(self):
        self.console.delete("1.0", "end")

if __name__ == "__main__":
    app = EliteSniffer()
    app.mainloop()
