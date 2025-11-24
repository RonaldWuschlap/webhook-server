# Webhook Server

A lightweight Python server built with Flask to receive webhooks from Sonarr/Radarr and trigger external API calls.

## Features

- **Sonarr & Radarr Support**: Dedicated handlers for media server events.
- **Configurable Endpoints**: Map webhook paths to specific handlers in `config.yaml`.
- **API Forwarding**: Trigger external APIs (e.g., Plex refresh, notifications) based on events.

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Edit `config.yaml` to define your webhooks and API clients.

```yaml
server:
  port: 5000

webhooks:
  - path: /webhook/sonarr
    handler: sonarr
    target_api: media_server

api_clients:
  media_server:
    url: "http://plex:32400/..."
    method: POST
    headers:
      X-Plex-Token: "YOUR_TOKEN"
```

## Usage

Start the server:

```bash
python -m app.main
```

## Project Structure

- `app/`: Main application code.
- `handlers/`: Action handlers for Sonarr/Radarr.
- `tests/`: Pytest verification scripts.
- `config.yaml`: Configuration file.
