# Webhook Server - Docker Deployment Guide

This guide explains how to deploy the webhook server on a Raspberry Pi 4B using Docker.

## Prerequisites

1. Raspberry Pi 4B with Raspberry Pi OS (64-bit recommended)
2. Docker and Docker Compose installed
3. Network access to your Jellyfin server and internet for ntfy.sh

## Installation

### 1. Install Docker on Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Reboot to apply group changes
sudo reboot
```

### 2. Deploy the Webhook Server

```bash
# Clone or copy the project to your Raspberry Pi
cd /home/pi/webhook-server

# Build and start the container
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Configuration

### Update config.yaml

Before deploying, ensure your `config.yaml` has the correct settings:

```yaml
api_clients:
  media_server_refresh:
    url: "http://192.168.178.164:8096/Library/Refresh"
    method: POST
    headers:
      Authorization: 'MediaBrowser Token="YOUR_JELLYFIN_TOKEN"'
      Content-Type: "application/json"
  
  notification_service:
    url: "https://ntfy.sh/stubenflix_alerts"
    method: POST
```

### Network Access

The webhook server will be accessible at:
- **Local network**: `http://<raspberry-pi-ip>:5000`
- **Webhook endpoints**:
  - Sonarr: `http://<raspberry-pi-ip>:5000/webhook/sonarr`
  - Radarr: `http://<raspberry-pi-ip>:5000/webhook/radarr`

## Docker Commands

```bash
# Start the container
docker-compose up -d

# Stop the container
docker-compose down

# View logs
docker-compose logs -f

# Restart after config changes
docker-compose restart

# Rebuild after code changes
docker-compose up -d --build

# Check container status
docker-compose ps
```

## Updating Configuration

The `config.yaml` file is mounted as a volume, so you can update it without rebuilding:

```bash
# Edit config
nano config.yaml

# Restart to apply changes
docker-compose restart
```

## Troubleshooting

### Check container logs
```bash
docker-compose logs -f webhook-server
```

### Test webhook endpoint
```bash
curl -X POST http://localhost:5000/webhook/sonarr \
  -H "Content-Type: application/json" \
  -d '{"eventType": "Test"}'
```

### Access container shell
```bash
docker-compose exec webhook-server /bin/bash
```

## Firewall Configuration

If you have a firewall enabled, allow port 5000:

```bash
sudo ufw allow 5000/tcp
```

## Auto-start on Boot

Docker Compose with `restart: unless-stopped` ensures the container starts automatically on system boot.

## Performance Notes

The Raspberry Pi 4B is more than capable of running this lightweight webhook server. Expected resource usage:
- **Memory**: ~50-100 MB
- **CPU**: Minimal (spikes only during webhook processing)
- **Storage**: ~200 MB for image and dependencies
