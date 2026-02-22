# 🧠 How It Works: SSH Honeypot & Active Defense

This document breaks down the technical architecture, logic, and capabilities of the SSH Honeypot project. It is designed to act as a technical reference for portfolio presentations or interviews.

## 1. The Core Architecture
The system is built on a containerized, two-tier architecture:
*   **The Trap (Cowrie)**: A high-interaction SSH and Telnet honeypot designed to log brute force attacks and the shell interaction performed by the attacker. It creates a fake file system and mimics a vulnerable server.
*   **The Monitor (Flask Dashboard)**: A Python/Flask backend that reads the JSON telemetry output from Cowrie in real-time, parses the attacker data, and renders it onto a modern web interface.

## 2. The Intrusion Detection System (IDS)
The dashboard isn't just a passive log viewer; it possesses an active monitoring thread.
*   **Log Tailing**: A background daemon continuously monitors `/cowrie/var/log/cowrie/cowrie.json`.
*   **Event Parsing**: It captures specific `eventid` types (e.g., `cowrie.login.success`, `cowrie.command.input`, `cowrie.session.file_download`).

## 3. The Active Defense & Response Engine
This is the standout feature of the project. Instead of just watching attackers, the system actively fights back.

### Real-Time Risk Scoring
Every action the attacker takes contributes to a dynamically calculated "Risk Score":
*   Logging in successfully: +50 points
*   Typing a command (e.g., `whoami`, `ls`): +10 points
*   Attempting to download malware (e.g., `wget`, `curl`): +40 points

### Automated Session Termination (Hard Logout)
When an attacker's Risk Score exceeds a defined threshold (e.g., 100), the system triggers an **Active Response**:
1.  **Detection**: The backend flags the IP as "Critical Risk".
2.  **Termination**: The Dashboard container (which has the Docker CLI installed and the Docker Socket mounted) executes `docker restart cowrie-honeypot`.
3.  **Result**: The SSH tunnel is instantly collapsed, kicking the attacker out of the environment forcefully.

### Reconnection Prevention (The Dead End)
To prevent the attacker from simply logging back in, the system enforces persistence:
*   The attacker's IP is added to a persistent `blocks.json` file.
*   The background monitor scans all incoming IP addresses. If an IP matches the blocklist, the system instantly restarts the honeypot container again, effectively making it impossible for the attacker to maintain a session. 

## 4. The UI & Telemetry (Glassmorphism)
The frontend is built with pure HTML/CSS/JS, utilizing a premium **Glassmorphism** aesthetic:
*   Translucent, frosted-glass panels over a dynamic gradient background.
*   Auto-refreshing intervals ensure the admin sees attacks happening in literal real-time.
*   The "Incident Response" tab allows administrators to manually terminate sessions or forgive (unblock) IPs.

## 5. Zero-Touch Deployment
To ensure seamless portability, the project features fully automated Multi-Platform deployment scripts (`win-setup.ps1` and `wsl-setup.sh`). 
*   The scripts automatically detect if Docker is installed (and install it if missing).
*   They fetch the latest code from GitHub and orchestrate the environment via `docker compose up -d`.
*   This proves an understanding of **DevOps**, **CI/CD principles**, and **Infrastructure as Code**.
