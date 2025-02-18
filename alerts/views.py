import requests
import platform
import subprocess
from django.http import JsonResponse
from django.conf import settings

TARGET_URL = "192.168.1.1"  # Change to your actual server IP

def check_network_status(request):
    """Ping the target server and send a Telex alert if down."""
    try:
        ping_flag = "-n" if platform.system().lower() == "windows" else "-c"
        response = subprocess.run(["ping", ping_flag, "1", TARGET_URL], capture_output=True, text=True)
        if response.returncode != 0:
            send_telex_alert("Network Down", f"Failed to reach {TARGET_URL}")
            return JsonResponse({"status": "down", "message": f"Failed to reach {TARGET_URL}"}, status=503)
        return JsonResponse({"status": "up", "message": f"Reached {TARGET_URL}"}, status=200)
    except Exception as e:
        send_telex_alert("Network Check Error", str(e))
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def send_telex_alert(title, message):
    """Send a real-time alert to Telex."""
    payload = {"title": title, "message": message}
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(settings.TELEX_WEBHOOK_URL, json=payload, headers=headers)
        if resp.status_code == 200:
            # Telex received OK
            pass
    except requests.exceptions.RequestException as e:
        print("Failed to send alert to Telex:", e)
