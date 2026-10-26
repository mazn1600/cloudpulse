# Deploy CloudPulse on AWS EC2

Stage 1 of the AWS phase: run the same Docker Compose stack, Nginx and SSH setup on one EC2 instance. There is no new application code; the server repeats what already runs in Ubuntu on WSL. Expect one to two hours.

```text
Internet → security group (80 open, 22 from my IP only)
         → EC2, Ubuntu 24.04 → Nginx :80 ─┬→ Next.js :3000 → FastAPI :8000 → PostgreSQL
                                           └→ FastAPI :8000 (/api/, /health, /ready)
```

Compose publishes ports 3000 and 8000 on the instance, but the security group keeps them closed, so Nginx on port 80 is the only public entry point. PostgreSQL stays inside the Compose network.

Commands marked PowerShell run on Windows; everything else runs on the server over SSH.

## 0. Set a cost guard first

1. Billing and Cost Management → Budgets → Create budget → template **Monthly cost budget**, amount `5` USD, your email.
2. Billing and Cost Management → Free Tier (or Credits): check which plan the account is on. Accounts created on or after 15 July 2025 spend credits; older accounts have the 12-month free tier.
3. Stop the instance when you are not using it, and terminate it when this stage is finished (section 10).

## 1. Choose a region

Use **Europe (Frankfurt) `eu-central-1`**. It is enabled by default and this stage stores no personal data.

For a real Saudi workload with personal data, data residency under PDPL decides the region. The nearest AWS options are Bahrain (`me-south-1`) and UAE (`me-central-1`); both are opt-in Regions that must be enabled under Account → AWS Regions before use. AWS has also announced a Saudi Region.

## 2. Import your SSH key

Use the ed25519 key created for the WSL SSH step. Print the public key and copy the whole line:

```powershell
Get-Content $HOME\.ssh\id_ed25519.pub
```

EC2 → Key pairs → Actions → **Import key pair** → name `cloudpulse-key` → paste the line → Import key pair.

## 3. Launch the instance

EC2 → Instances → **Launch instances**:

| Setting | Value |
|---|---|
| Name | `cloudpulse-server` |
| AMI | Ubuntu Server 24.04 LTS, 64-bit (x86) |
| Instance type | The one marked **Free tier eligible** (t3.micro or t2.micro, 1 GiB memory) |
| Key pair | `cloudpulse-key` |
| Network settings | Create security group. **Allow SSH traffic from: My IP**. Tick **Allow HTTP traffic from the internet**. Leave HTTPS unticked |
| Storage | 20 GiB gp3 (the default 8 GiB is too small for the images plus swap) |

Do not add rules for 3000, 8000 or 5432. Launch, wait until the instance is **Running** and its status checks pass, then copy its **Public IPv4 address**.

## 4. Connect

```powershell
ssh -i $HOME\.ssh\id_ed25519 ubuntu@<PUBLIC_IP>
```

Ubuntu AMIs log in as `ubuntu`. Answer `yes` to the fingerprint prompt the first time.

## 5. Prepare the server

Update packages and add 2 GiB of swap. Without swap, a 1 GiB instance can run out of memory while building the Next.js image.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

If `apt upgrade` shows a dialog about restarting services, accept the defaults.

Install Docker Engine and the Compose plugin from Docker's apt repository (from `docs.docker.com/engine/install/ubuntu`):

```bash
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
exit
```

Reconnect (section 4) so the `docker` group applies, then check:

```bash
docker compose version
```

## 6. Run CloudPulse

```bash
git clone https://github.com/mazn1600/cloudpulse.git
cd cloudpulse
docker compose up -d --build
docker compose ps -a
```

The first build takes several minutes on a micro instance. `migrate` should show `Exited (0)`, `db` and `backend` should be `healthy`, and `frontend` should be `Up`. Check the API from the server:

```bash
curl -i http://localhost:8000/ready
```

## 7. Nginx and SSH hardening

The same steps as on WSL, with the repository already on the server:

```bash
sudo apt install -y nginx
sudo cp ~/cloudpulse/deploy/nginx/cloudpulse.conf /etc/nginx/sites-available/cloudpulse
sudo ln -s /etc/nginx/sites-available/cloudpulse /etc/nginx/sites-enabled/cloudpulse
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```

Ubuntu AMIs already refuse password logins; the repository config makes that explicit and blocks root:

```bash
sudo cp ~/cloudpulse/deploy/ssh/00-cloudpulse-hardening.conf /etc/ssh/sshd_config.d/
sudo sshd -t && sudo systemctl reload ssh
```

Keep this session open and test a new login from a second PowerShell window before closing it.

## 8. Verify from your PC

```powershell
curl.exe -i http://<PUBLIC_IP>/health
curl.exe -i http://<PUBLIC_IP>/ready
curl.exe -m 5 http://<PUBLIC_IP>:8000/health
```

The first two return HTTP 200. The third must time out: the security group blocks port 8000, so the API is only reachable through Nginx. Then open `http://<PUBLIC_IP>/` in the browser.

## 9. Record the deployment

From `~/cloudpulse` on the server:

```bash
docker compose exec db psql -U cloudpulse -c "INSERT INTO deployments (version, environment, status) VALUES ('v0.2.0', 'aws-ec2', 'successful');"
```

Refresh the dashboard: `v0.2.0` in `aws-ec2` appears at the top of Recent deployments.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ssh: connect ... Connection timed out` | Your public IP changed, so the "My IP" rule no longer matches | EC2 → Security groups → the instance's group → Edit inbound rules → SSH source → My IP |
| `Permission denied (publickey)` | Wrong user or key | User is `ubuntu`; use the private key that matches the imported public key |
| `permission denied while trying to connect to the Docker daemon socket` | The `docker` group change has not applied | `exit` and reconnect |
| Build stops with `Killed` or exit code 137 | Out of memory | `free -h` must show the swap; rerun `docker compose up -d --build` |
| Browser hangs on `http://<PUBLIC_IP>` | No HTTP rule in the security group | Add inbound HTTP (80) from Anywhere |
| `502 Bad Gateway` | Nginx is up but an app behind it is not | `docker compose ps -a`, then `docker compose logs backend` or `frontend` |
| Dashboard shows "API unavailable" | Backend not ready or migrations failed | `curl -i http://localhost:8000/ready` on the server, then `docker compose logs migrate` |
| `no space left on device` | Disk full | `df -h`; `docker system prune` removes unused images and build cache |
| New public IP after a restart | Stopping releases the public IPv4 address | Use the new address from the console; an Elastic IP keeps a fixed one but is billed |

## 10. Stop paying when done

- **Pause:** Instance state → Stop. Compute charges stop; the 20 GiB disk is still billed, and the public IP changes on the next start.
- **Finish:** Instance state → Terminate. This deletes the instance and its disk. Delete the key pair and security group too if you will not reuse them.

## What this stage proves, and what comes next

This stage proves the stack runs on cloud infrastructure with a single public entry point, and that SSH accepts keys only, from one IP.

Next, in order:

1. Build the images in GitHub Actions and push them to Amazon ECR, authenticating with GitHub OIDC so no AWS keys are stored in the repository. The server then pulls images instead of building them.
2. Move PostgreSQL to Amazon RDS in a private subnet, with the password in AWS Secrets Manager instead of `compose.yaml`.
3. Add a domain and HTTPS: Let's Encrypt on Nginx, or a load balancer with an ACM certificate.
4. Describe the security group and instance in Terraform instead of console clicks.
5. Bind the published ports in `compose.yaml` to `127.0.0.1`, so 3000 and 8000 stay private even if a security group rule is opened by mistake.
