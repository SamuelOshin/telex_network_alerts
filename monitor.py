import time
import requests

CHECK_URL = "https://your-render-app.onrender.com/check/"

while True:
    try:
        response = requests.get(CHECK_URL)
        print("Checked:", response.json())
    except Exception as e:
        print("Error:", e)
    
    time.sleep(300)  # Run every 5 minutes
