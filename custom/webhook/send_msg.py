#!/usr/bin/env python3
import requests
import sys

TELEGRAM_BOT_TOKEN = "7718476856:AAG45fi-GQU8RSLCwCvZYIGmy8Ee37Fc4mk"
TELEGRAM_CHAT_ID = "512741129"

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, json=data)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_message(" ".join(sys.argv[1:]))
