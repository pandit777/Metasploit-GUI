import customtkinter as ctk
from scapy.all import sniff, IP, TCP, UDP
import threading

class CyberSniffer(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ Cyber Sniffer - Mini Wireshark")
        self.geometry("800x600")
        ctk.set_appearance_mode("Dark")

        # Control Buttons
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=20, padx=20, fill="x")

        self.start_btn = ctk.CTkButton(self.btn_frame, text="▶ Start Sniffing", fg_color="green", command=self.start_sniffing)
        self.start_btn.grid(row=0, column=0, padx=10)

        self.stop_btn = ctk.CTkButton(self.btn_frame, text="⏹ Stop", fg_color="red", command=self.stop_sniffing)
        self.stop_btn.grid(row=0, column=1, padx=10)

        # Console for Packets
        self.console = ctk.CTkTextbox(self, width=750, height=450, font=("Consolas", 12))
        self.console.pack(pady=10, padx=20)
        
        self.sniffing = False

    def packet_callback(self, packet):
        if not self.sniffing:
            return
        
        if packet.haslayer(IP):
            src = packet[IP].src
            dst = packet[IP].dst
            proto = "TCP" if packet.haslayer(TCP) else "UDP" if packet.haslayer(UDP) else "Other"
            
            log_msg = f"[+] {proto} | Source: {src} -> Dest: {dst}\n"
            self.console.insert("end", log_msg)
            self.console.see("end")

    def sniff_packets(self):
        sniff(prn=self.packet_callback, stop_filter=lambda x: not self.sniffing, store=0)

    def start_sniffing(self):
        self.sniffing = True
        self.console.insert("end", "[*] Sniffing Started...\n")
        threading.Thread(target=self.sniff_packets, daemon=True).start()

    def stop_sniffing(self):
        self.sniffing = False
        self.console.insert("end", "[!] Sniffing Stopped.\n")

if __name__ == "__main__":
    app = CyberSniffer()
    app.mainloop()
