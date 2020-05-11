import requests
import json
from collections import defaultdict

URL = "https://api.wasiliana.com/api/v1/developer/sms/bulk/send/sms/request"
WS_API_KEY = ""
SENDER_ID = ""
FROM = SENDER_ID


def send_message(FROM=FROM, RECIPIENTS=[], MESSAGE=""):
    headers = {
        "Content-Type": "application/json;",
        "Accept": "application/json",
        "apiKey": WS_API_KEY,
    }
    payload = defaultdict()
    payload["from"] = FROM
    payload["recipients"] = RECIPIENTS
    payload["message"] = MESSAGE
    payload = dict(payload)
    payload = json.loads(str(payload))
    response = requests.request("POST", URL, data=payload, headers=headers)
    print(response.json())
    return response.json()
