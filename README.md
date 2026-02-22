# 🛡️ SSH Honeypot: Active Defense & Response

A hardened, high-interaction **Cowrie** honeypot integrated with an **Advanced Analytics Dashboard**. This system doesn't just watch threats—it actively neutralizes them through real-time risk scoring and automated session termination.

---

## 💎 Key Features

- **🚀 Active Session Kill**: Instantly terminates intruder shells via container restart when high-risk commands (`curl`, `wget`, `bash`) are detected.
- **🤖 Background Threat Monitor**: A 24/7 internal monitor in `app.py` processes logs every 5 seconds, ensuring defense actions trigger even without UI activity.
- **🚫 Persistent Auto-Blocking**: Malicious IPs are added to a permanent blocklist (`blocked_ips.json`) and aggressively kicked if they attempt to reconnect.
- **✨ Glassmorphic UI**: A modern, responsive dashboard with real-time telemetry, risk badges, and a dedicated **Incident Response** control center.
- **🐳 Fully Containerized**: Seamlessly managed via Docker Compose with streamlined volume sharing for log persistence.

---

## 📂 Project Structure

- `dashboard/`: Flask backend with background monitoring thread and glassmorphic frontend.
- `cowrie/`: Hardened configuration for the high-interaction SSH engine.
- `docker-compose.yml`: Orchestration for the honeypot and the defense engine.

---

## 🛠️ Multi-Platform Setup

Automate your environment setup on Windows and WSL using the provided scripts.

### 🪟 Windows (PowerShell)
Setup your Windows environment with Alacritty, Git, and Starship.
```powershell
# Run the installer
.\win-setup.ps1
```

### 🐧 WSL (Ubuntu)
Standardize your WSL terminal with Zsh, Oh-My-Zsh, and Neovim.
```bash
# Run the installer
chmod +x wsl-setup.sh
./wsl-setup.sh
```

---

## 🚀 Quick Start (Docker)

### 1. Launch the System
```bash
docker compose up -d
```

### 2. Access the Defense Center
View live statistics and manage incidents at:
👉 **[http://localhost:5001](http://localhost:5001)**

### 3. Test Active Defense
Simulate an attack to see the system in action:
```bash
# 1. Connect to the honeypot
ssh -p 2222 root@localhost

# 2. Trigger the defense engine inside the honeypot
curl http://malicious-test.com
```
**Outcome**: Your SSH session will be **dropped instantly**. If you try to reconnect, the background monitor will recognize your blocked IP and kick you immediately.

---

## 🛡️ Incident Response logic
The dashboard categorizes events into risk levels:
- **🔴 High Risk (70-100)**: Triggers immediate session termination and permanent IP block.
- **🟠 Medium Risk (30-69)**: Flagged in the Incident Response tab for manual review.
- **🔵 Low Risk (1-29)**: Standard reconnaissance or login failures.

---

## 🚨 Maintenance & Operations
- **Follow Logs**: `docker compose logs -f dashboard`
- **Reset Defense**: Delete `dashboard/blocked_ips.json` and restart the dashboard.
- **Stop System**: `docker compose down`

---
**Disclaimer**: This project is for educational and research purposes only. Use ethically.
