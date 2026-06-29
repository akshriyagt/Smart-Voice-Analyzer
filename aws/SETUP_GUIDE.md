# 🚀 CI/CD Setup Guide - Smart Voice Analyzer

## What happens automatically after setup:
```
You push code to GitHub
        ↓
GitHub Actions runs (auto)
        ↓
Tests your code ✅
        ↓
Builds Docker image 🐳
        ↓
Pushes to DockerHub
        ↓
SSH into your EC2
        ↓
Deploys new version 🚀
        ↓
Health check confirms live ✅
```

---

## STEP 1: DockerHub Account
1. Go to https://hub.docker.com
2. Sign up (free)
3. Create repository: `smart-voice-analyzer`
4. Go to Account Settings → Security → New Access Token
5. Copy the token

---

## STEP 2: AWS EC2 Setup
1. AWS Console → EC2 → Launch Instance
2. Choose: Ubuntu 22.04 LTS
3. Instance type: t3.small (or t2.micro for free tier)
4. Storage: 20GB
5. Security Group - open ports:
   - 22 (SSH)
   - 80 (HTTP)
6. Download key pair (.pem file) — SAVE IT SAFELY!
7. Launch instance
8. Copy the Public IP

### SSH into EC2 and run setup:
```bash
# Windows (use Git Bash or WSL)
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Once inside EC2, run:
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/smart-voice-analyzer/main/aws/ec2_setup.sh
bash ec2_setup.sh
```

---

## STEP 3: GitHub Repository
1. Go to https://github.com → New repository
2. Name: `smart-voice-analyzer`
3. Push your project:
```bash
cd smart_voice_analyzer_v2
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/YOUR_USERNAME/smart-voice-analyzer.git
git push -u origin main
```

---

## STEP 4: GitHub Secrets (MOST IMPORTANT)
Go to GitHub repo → Settings → Secrets → Actions → New secret

Add these 4 secrets:

| Secret Name | Value |
|---|---|
| `DOCKERHUB_USERNAME` | your dockerhub username |
| `DOCKERHUB_TOKEN` | your dockerhub access token |
| `EC2_HOST` | your EC2 public IP (e.g. 13.235.xx.xx) |
| `EC2_SSH_KEY` | contents of your .pem file (open in notepad, copy all) |

---

## STEP 5: Push and Watch Magic! 🎉
```bash
git add .
git commit -m "trigger deploy"
git push origin main
```

Go to GitHub → Actions tab → Watch it deploy automatically!

---

## Your app will be live at:
```
http://YOUR_EC2_IP
```
