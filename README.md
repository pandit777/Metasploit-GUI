# ⚡ Elite Payload & C2 Command Center

A professional, modern GUI-based tool built with Python for automating Metasploit payload generation, APK binding, and real-time session handling.

## ✨ Features
- **Modern UI:** Dark/Light mode support with CustomTkinter.
- **Multi-OS Support:** Generate payloads for Android, Windows, iOS, and macOS.
- **APK Binder:** Bind payloads with original APK files to bypass suspicion.
- **Auto-Signing:** Integrated V2/V3 signing using `apksigner` for Android 11+ compatibility.
- **Link Generator:** Built-in local web server to host payloads for easy target download.
- **Live C2 Console:** Real-time logging and Metasploit RPC integration for session management.
- **Telegram Notify:** Instant alerts on your phone when a payload is generated.

## 🛠️ Prerequisites (System Setup)
Before running the tool, ensure your Kali Linux is updated and has the necessary tools:

```bash
# Update System
sudo apt update && sudo apt upgrade -y

# Install Metasploit Framework
sudo apt install metasploit-framework -y

# Install JDK, Apksigner, and Zipalign
sudo apt install default-jdk apksigner zipalign apktool -y
```

> **Note:** Ensure you have **Apktool v2.9.3+** installed for modern APK binding.

## 🚀 Installation

1. **Clone or Download** this repository.
2. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```

## ⚙️ How to Use

1. **Start Metasploit RPC Server:**
   Open a terminal and run the RPC server so the GUI can communicate with Metasploit:
   ```bash
   msfrpcd -P 1234 -S -f
   ```

2. **Launch the Tool:**
   ```bash
   python3 main.py
   ```

3. **Generate Payload:**
   - Select the **Target OS**.
   - (Optional) Select an **Original APK** to bind.
   - Enter your **LHOST** (IP) and **LPORT**.
   - Click **Build & Deploy Link**.
   - Copy the generated URL and share it with the target.

4. **Start Listening:**
   - Click **Start Live Listener** to wait for incoming connections.

## 📂 Project Structure
- `main.py`: The primary GUI application.
- `requirements.txt`: Python library dependencies.
- `my-release-key.keystore`: (Auto-generated) Digital key for signing APKs.

## ⚠️ Disclaimer
*This tool is developed for **educational purposes** and **authorized security testing** only. Using this tool for attacking targets without prior mutual consent is illegal. The developer is not responsible for any misuse or damage caused by this program.*
