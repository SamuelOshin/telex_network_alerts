import requests
import platform
import subprocess
import socket
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

TARGET_URL = "192.168.1.1"  # Change to your actual server IP

def check_network_status(request):
    """Attempt a socket connection instead of using ping."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TARGET_URL, 80))
        s.close()
        return JsonResponse({"status": "up", "message": f"Reached {TARGET_URL}"}, status=200)
    except Exception as e:
        send_telex_alert("Network Down", f"Failed to reach {TARGET_URL}")
        return JsonResponse({"status": "down", "message": f"Failed to reach {TARGET_URL}"}, status=503)

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

@csrf_exempt
def handle_telex_json(request):
    """Handle Returning Telex JSON."""
    if request.method == "GET":
        return JsonResponse(
            {
                "data": {
                    "date": {
                        "created_at": "2025-02-18",
                        "updated_at": "2025-02-18"
                    },
                    "descriptions": {
                        "app_name": "Network Downtime Alerts",
                        "app_description": "Checks network connectivity at intervals, sends alerts on downtime.",
                        "app_logo": "https://telex-network-alerts.onrender.com",
                        "app_url": "https://telex-network-alerts.onrender.com/alerts/check",
                        "background_color": "#fff"
                    },
                    "is_active": True,
                    "key_features": [
                    "Periodically checks server or endpoint availability.",
                    "Sends real-time alerts to Telex on downtime.",
                    "Configurable check interval via Cron expression.",
                    "Lightweight solution without a database."
                    ],
                    "permissions": {
                    "monitoring_user": {
                        "always_online": True,
                        "display_name": "Network Monitor"
                    }
                    },
                    "author": "Bobbysam",
                    "integration_category": "Monitoring",
                    "settings": [
                        {
                            "label": "interval",
                            "type": "text",
                            "required": True,
                            "default": "* * * * *"
                        },
                         {
                            "label": "Do you want to continue",
                            "type": "checkbox",
                            "required": True,
                            "default": "Yes"
                        },
                    ],
                    "tick_url": "https://telex-network-alerts.onrender.com/alerts/check"
                }
            }
        )
