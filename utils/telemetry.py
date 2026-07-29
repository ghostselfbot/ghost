import requests
import sys

from utils import Config, VERSION, console

API_URL = "https://benny.fun/api/ghost/ping"
cfg = Config()

def send_telemetry_ping():
    if not cfg.get("telemetry"):
        return
    
    install_id = cfg.get("install_id")
    platform = sys.platform
    python_version = sys.version

    payload = {
        "install_id": install_id,
        "version": VERSION,
        "platform": platform,
        "python": python_version
    }
    
    try:
        response = requests.post(API_URL, headers={"Content-Type": "application/json", "User-Agent": f"Ghost/{VERSION}"}, json=payload, timeout=5)
        response.raise_for_status()
        if not cfg.get_headless():
            print("[TELEMETRY] Telemetry ping sent successfully.")
        else:
            console.info("Telemetry ping sent successfully.")
    except requests.exceptions.RequestException as e:
        if not cfg.get_headless():
            print(f"[TELEMETRY] Failed to send telemetry ping: {e}")
        else:
            console.error(f"Failed to send telemetry ping: {e}")