# 🧠 Tech Stack & Architecture: SSH Honeypot Active Defense

This document breaks down the exact technologies, libraries, and architecture used to build the SSH Honeypot. It is designed to act as a technical reference for portfolio presentations or interviews.

## 🛠️ Complete Tech Stack & Libraries

### Core Infrastructure
*   **Docker Engine & Docker Compose**: Used for complete containerization of the honeypot and the dashboard. Crucially, the Docker Socket (`/var/run/docker.sock`) is mounted into the dashboard container to allow the Python backend to execute host-level Docker commands (Active Defense).
*   **Cowrie Honeypot**: A highly customizable, medium-to-high interaction SSH and Telnet honeypot designed to log brute force attacks and shell interaction.

### Backend & Monitoring Logic
*   **Language**: Python 3.10+
*   **Web Framework**: `Flask==3.0.0` (Chosen for its lightweight footprint and rapid API development capabilities to serve the dashboard).
*   **Daemon Threads**: Python's native `threading` module is used to run a background daemon that continually monitors and parses the `cowrie.json` logs in real-time without blocking the web server.
*   **File I/O**: Python's native `json` and `os` libraries are utilized for high-performance log tailing and managing the persistent `blocks.json` database.

### Frontend
*   **Markup / Styling**: Pure HTML5 and Vanilla CSS3.
*   **Design Paradigm**: Premium **Glassmorphism** aesthetic utilizing `backdrop-filter: blur()`, CSS variables for dynamic theming, and smooth CSS transitions.
*   **Interactivity**: Vanilla JavaScript (ES6) utilizing the Fetch API (`fetch()`) to asynchronously poll the Flask backend for live telemetry updates without page reloads.

### Deployment Automation
*   **Bash / Shell**: For the `wsl-setup.sh` zero-touch Linux deployment script (utilizing `curl`, `apt-get`, and `usermod`).
*   **PowerShell**: For the `win-setup.ps1` zero-touch Windows deployment script (utilizing `winget`, `Invoke-RestMethod`, and ErrorAction preference control).

---

## 🏗️ The Active Defense Architecture

The dashboard isn't just a passive log viewer; it possesses an active monitoring thread that fights back.

### 1. Real-Time Risk Scoring
Every action the attacker takes contributes to a dynamically calculated "Risk Score":
*   Logging in successfully: +50 points
*   Typing a command (e.g., `whoami`, `ls`): +10 points
*   Attempting to download malware (e.g., `wget`, `curl`): +40 points

### 2. Automated Session Termination (Hard Logout)
When an attacker's Risk Score exceeds a defined threshold (e.g., 100), the system triggers an **Active Response**:
1.  **Detection**: The backend flags the IP as "Critical Risk".
2.  **Termination**: The Dashboard container uses the `subprocess` library to execute `docker restart cowrie-honeypot` via the mounted Docker socket.
3.  **Result**: The SSH tunnel is instantly collapsed, kicking the attacker out of the environment forcefully.

### 3. Reconnection Prevention (The Dead End)
To prevent the attacker from simply logging back in, the system enforces persistence:
*   The attacker's IP is added to a persistent `blocks.json` file.
*   The background monitor streams all incoming connection attempts. If an IP matches the blocklist, the system instantly drops the connection engine again.
