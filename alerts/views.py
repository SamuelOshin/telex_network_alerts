import requests
import platform
import subprocess
import socket
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from functools import lru_cache
from datetime import datetime
from urllib.parse import urlparse
from django.views.decorators.http import require_http_methods
import validators

TARGET_URL = settings.TARGET_URL

# Add this variable to track last known state
last_known_state = {"status": "unknown", "last_check": None}

@csrf_exempt
@require_http_methods(["GET", "POST"])
def check_network_status(request):
    """Attempt a socket connection instead of ping."""
    global last_known_state
    current_time = datetime.now()
    
    try:
        # Use the dynamically set TARGET_URL
        target_url = settings.TARGET_URL
        parsed_url = urlparse(target_url)
        hostname = parsed_url.netloc or parsed_url.path
        port = 443 if parsed_url.scheme == 'https' else 80
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((hostname, port))
        s.close()
        
        # Check if status was previously down and now up (restored)
        if last_known_state["status"] == "down":
            send_telex_alert(
                "Network Restored", 
                f"Connection to {target_url} has been restored",
                status="success"
            )
        
        last_known_state = {"status": "up", "last_check": current_time}
        return JsonResponse({"status": "up", "message": f"Reached {target_url}"}, status=200)
    
    except Exception as e:
        last_known_state = {"status": "down", "last_check": current_time}
        send_telex_alert(
            "Network Down", 
            f"Failed to reach {target_url}",
            status="error"
        )
        return JsonResponse({"status": "down", "message": f"Failed to reach {target_url}"}, status=503)

def send_telex_alert(title, message, status="error"):
    """Send a real-time alert to Telex."""
    payload = {
        "event_name": title,
        "message": message,
        "status": status,  # Now accepts status as parameter
        "username": "Bobbysam"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(settings.TELEX_WEBHOOK_URL, json=payload, headers=headers)
        print(f"Response status: {resp.status_code}")
        response_data = resp.json()
        print(f"Response body: {response_data}")
        
        if resp.status_code in [200, 202]:
            print(f"Alert sent to Telex successfully. Task ID: {response_data.get('task_id')}")
            return True
        else:
            print(f"Telex returned unexpected status code: {resp.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Failed to send alert to Telex: {str(e)}")
        return False

@csrf_exempt
@require_http_methods(["GET", "POST"])
def handle_telex_json(request):
    """Handle Returning Telex JSON."""
    base_url = request.build_absolute_uri('/').rstrip('/')
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
                        "app_logo": "https://img.freepik.com/free-vector/automatic-backup-abstract-concept-illustration_335657-1834.jpg?t=st=1739910156~exp=1739913756~hmac=430c269845ae9683d5f93884d28ef5b053169b5a8ddab1d7f49f212e34f0af52&w=740",
                        "app_url": base_url,
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
                    "integration_category": "Monitoring & Logging",
                    "integration_type": "interval",
                    "settings": [
                        {
                            "label": "Target URL to Monitor",
                            "key": "target_url",
                            "type": "text",
                            "required": True,
                            "default": "https://your-server-url.com",
                            "description": "The URL of the server you want to monitor for downtime"
                        },
                        {
                            "label": "interval",
                            "type": "dropdown",
                            "required": True,
                            "default": "* * * * *"
                            "options": ["* * * * *", "*/5 * * * *", "*/10 * * * *", "*/15 * * * *", "*/30 * * * *", "0 * * * *", "0 */2 * * *", "0 */4 * * *", "0 */6 * * *", "0 */12 * * *"]
                            "description": "The interval to check the server for downtime"
                        },
                    ],
                    "tick_url": f"{base_url}/tick",
                    "target_url": ""
                }
            }
        )

@csrf_exempt
def configure_webhook(request):
    """Handle webhook configuration from Telex."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            target_url = data.get('target_url')
            
            # Validate URL format
            if not validators.url(target_url):
                return JsonResponse({
                    "status": "error",
                    "message": "Invalid URL format"
                }, status=400)
            
            # Test connection
            try:
                response = requests.head(target_url, timeout=5)
                response.raise_for_status()
            except requests.RequestException:
                return JsonResponse({
                    "status": "error",
                    "message": "Could not connect to target URL"
                }, status=400)
            
            settings.TARGET_URL = target_url
            return JsonResponse({
                "status": "success",
                "message": "Target URL configured successfully"
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON data"
            }, status=400)
    
    return JsonResponse({
        "status": "error",
        "message": "Method not allowed"
    }, status=405)
