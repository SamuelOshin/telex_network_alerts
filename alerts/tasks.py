import os
import requests
import subprocess
from celery import Celery
from django.conf import settings

# Initialize Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
app = Celery('your_project')
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()

# Target server to check
TARGET_URL = "8.8.8.8"  
TELEX_WEBHOOK_URL = "https://your-telex-webhook-url.com"  # Replace with actual webhook URL

@app.task
def check_network_status():
    """Check network connectivity and send an alert if the server is unreachable."""
    try:
        response = subprocess.run(["ping", "-c", "1", TARGET_URL], capture_output=True, text=True)
        if response.returncode != 0:
            send_telex_alert("Network Down", f"Failed to reach {TARGET_URL}\n{response.stderr}")
    except Exception as e:
        send_telex_alert("Network Check Error", str(e))

def send_telex_alert(title, message):
    """Send an alert to Telex."""
    payload = {
        "title": title,
        "message": message
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(TELEX_WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Failed to send alert to Telex:", e)
