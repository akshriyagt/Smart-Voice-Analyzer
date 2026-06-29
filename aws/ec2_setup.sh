#!/bin/bash
# ═══════════════════════════════════════════════
# Smart Voice Analyzer - AWS EC2 First Time Setup
# Run this ONCE after launching EC2 instance
# ═══════════════════════════════════════════════

echo "=== Installing Docker ==="
sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose curl git
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu

echo "=== Creating project folder ==="
sudo mkdir -p /opt/smart-voice-analyzer
sudo chown ubuntu:ubuntu /opt/smart-voice-analyzer
cd /opt/smart-voice-analyzer

echo "=== Creating required folders ==="
mkdir -p uploads archive spam_files notspam_files normal_files

echo "=== Creating empty data files ==="
echo "[]" > records.json
echo "{}" > users.json

echo "=== Done! ==="
echo "Now push code to GitHub — CI/CD will auto deploy!"
echo "Your server IP: $(curl -s ifconfig.me)"
