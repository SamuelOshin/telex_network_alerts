import time
import requests

CHECK_URL = "https://telex-network-alerts.onrender.com/alerts/check/"

while True:
    try:
        response = requests.get(CHECK_URL)
        print("Checked:", response.json())
    except Exception as e:
        print("Error:", e)
    
    time.sleep(60)  # Run every 60 seconds
