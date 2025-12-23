import requests
import time

BOT_TOKEN = "BOT_TOKEN"

UPDATE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
SEND_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


offset = None

while True:
        params = {"timeout": 100}
        if offset:
                params["offset"] = offset

        resp = requests.get(UPDATE_URL, params=params).json()

        for update in resp["result"]:
                offset = update["update_id"] + 1
                print(update)
                payload = {"chat_id": update["message"]["chat"]["id"], "text": update["message"]["text"]}
                requests.post(SEND_URL, payload)

        time.sleep(1)
