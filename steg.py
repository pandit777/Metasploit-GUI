import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import subprocess

class StegoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ethical Hacking: Stego Tool")
        self.geometry("600x500")
        ctk.set_appearance_mode("dark")

        # UI Layout
        self.label = ctk.CTkLabel(self, text="Payload Hider (Image/Audio)", font=("Arial", 24, "bold"))
        self.label.pack(pady=20)

        # 1. Payload Selection
        self.payload_path = ""
        self.btn_payload = ctk.CTkButton(self, text="1. Select Payload (.apk / .exe)", command=self.select_payload)
        self.btn_payload.pack(pady=10)

        # 2. Cover File Selection
        self.cover_path = ""
        self.btn_cover = ctk.CTkButton(self, text="2. Select Cover File (JPG/WAV)", command=self.select_cover)
        self.btn_cover.pack(pady=10)

        # 3. Password Entry
        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Enter Stego Password", show="*")
        self.pass_entry.pack(pady=10)

        # 4. Action Button
        self.btn_execute = ctk.CTkButton(self, text="Embed Payload", fg_color="green", command=self.embed_data)
        self.btn_execute.pack(pady=30)

        # Output Box
        self.output_text = ctk.CTkTextbox(self, width=500, height=100)
        self.output_text.pack(pady=10)

    def select_payload(self):
        self.payload_path = filedialog.askopenfilename(title="Select Payload")
        self.log(f"Payload Selected: {os.path.basename(self.payload_path)}")

    def select_cover(self):
        self.cover_path = filedialog.askopenfilename(title="Select Cover File")
        self.log(f"Cover File Selected: {os.path.basename(self.cover_path)}")

    def log(self, message):
        self.output_text.insert("end", message + "\n")

    def embed_data(self):
        if not self.payload_path or not self.cover_path or not self.pass_entry.get():
            messagebox.showerror("Error", "Please fill all fields!")
            return

        password = self.pass_entry.get()
        # Steghide Command
        # -ef: embed file, -cf: cover file, -p: password
        command = f"steghide embed -ef '{self.payload_path}' -cf '{self.cover_path}' -p '{password}'"
        
        try:
            self.log("Processing...")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log("SUCCESS: Payload hidden inside cover file!")
                messagebox.showinfo("Success", "Payload Embedded Successfully!")
            else:
                self.log(f"ERROR: {result.stderr}")
        except Exception as e:
            self.log(f"System Error: {str(e)}")

if __name__ == "__main__":
    app = StegoApp()
    app.mainloop()
