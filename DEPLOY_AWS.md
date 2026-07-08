# Deploying to AWS (single EC2 server) + CI/CD

This sets up **one server on AWS** that runs everything (backend + Ollama +
frontend), reachable at a public URL 24/7 — and every time you push code to
GitHub, it automatically redeploys itself.

---

## Part 1 — Create the EC2 server (one-time, AWS Console)

1. Log into https://console.aws.amazon.com → search **EC2** → **Launch instance**
2. **Name**: `smart-voice-analyzer`
3. **AMI**: Ubuntu Server 24.04 LTS
4. **Instance type**: `t3.large` or bigger (Whisper + Ollama need real RAM —
   don't use the free-tier `t2.micro`, it will be too slow/small; expect
   roughly $60-70/month for a t3.large running 24/7, less if you stop it
   when not in use)
5. **Key pair**: Create new → name it `smart-voice-key` → download the
   `.pem` file and keep it safe (you can't re-download it later)
6. **Network settings** → Edit → Add these inbound rules:
   - SSH (port 22) — source: My IP
   - Custom TCP, port 8000 — source: Anywhere (0.0.0.0/0) — this is how
     the app will be reached publicly
7. **Storage**: bump to at least 20 GB (Whisper + Ollama models need space)
8. Click **Launch instance**
9. Once it's running, copy its **Public IPv4 address** — this is your app's
   address, e.g. `http://54.123.45.67:8000`

---

## Part 2 — First-time server setup (one-time, via SSH)

Open a terminal and connect (on Windows, use PowerShell or WSL):
```bash
ssh -i smart-voice-key.pem ubuntu@<your-ec2-public-ip>
```

Once connected, run:
```bash
# System basics
sudo apt update && sudo apt install -y python3.12-venv git

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:1b

# Clone your project (push it to GitHub first, see Part 3)
git clone https://github.com/<your-username>/smart-voice-analyzer.git
cd smart-voice-analyzer/backend

# Python setup
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set up the systemd service so it runs permanently and restarts on reboot:
```bash
sudo cp ../deploy/smart-voice-analyzer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable smart-voice-analyzer
sudo systemctl start smart-voice-analyzer
```

Check it's running:
```bash
sudo systemctl status smart-voice-analyzer
curl http://localhost:8000/health
```

Now open `http://<your-ec2-public-ip>:8000` in any browser, from anywhere —
the app should load.

---

## Part 3 — Set up GitHub + CI/CD (one-time)

1. Push this whole project to a new GitHub repo:
```bash
cd smart-voice-analyzer
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/smart-voice-analyzer.git
git push -u origin main
```

2. In your GitHub repo → **Settings → Secrets and variables → Actions** →
   add these three **repository secrets**:
   - `EC2_HOST` → your EC2 public IP (e.g. `54.123.45.67`)
   - `EC2_USER` → `ubuntu`
   - `EC2_SSH_KEY` → the full contents of your `smart-voice-key.pem` file
     (open it in a text editor and paste everything, including the
     `-----BEGIN...` and `-----END...` lines)

The workflow file (`.github/workflows/deploy.yml`) is already included in
this project — GitHub will pick it up automatically once you push.

---

## Part 4 — Using it going forward

From now on, whenever you make a code change:
```bash
git add .
git commit -m "describe your change"
git push
```
GitHub Actions will automatically SSH into your EC2 server, pull the new
code, reinstall any new dependencies, and restart the app — no manual
redeploying needed.

Check progress under your GitHub repo's **Actions** tab.

---

## Notes

- **Cost**: EC2 charges by the hour while running. Stop the instance from
  the AWS Console when you're not using it to avoid ongoing charges (its
  public IP will change when you restart it, unless you attach an
  [Elastic IP](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html)).
- **HTTPS**: this setup uses plain `http://` on port 8000. For a proper
  domain with HTTPS later, you'd add Nginx + a free SSL cert (Let's
  Encrypt) in front of it — a good next step once the basic version works.
- **Security**: opening port 8000 to "Anywhere" means anyone with the link
  can use your app. That's fine for testing/sharing, but for anything
  more sensitive you'd want authentication in front of it.
