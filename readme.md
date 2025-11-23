# Webhook Server

A lightweight Python server built with Flask to receive webhooks and trigger local scripts or external API calls based on the content.

## Features

- **Configurable Endpoints**: Define routes, methods, and actions in `config.yaml`.
- **Script Execution**: Trigger shell commands or scripts with payload data.
- **API Forwarding**: Forward webhooks to other APIs or services.
- **Lightweight**: Minimal dependencies (Flask, PyYAML, Requests).

## Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Edit `config.yaml` to define your endpoints. Example:

```yaml
port: 5000
endpoints:
  - path: /webhook/deploy
    method: POST
    actions:
      - type: script
        command: "echo 'Deploying...'"
```

## Usage

Start the server:

```bash
python -m app.main
```

Send a webhook:

```bash
curl -X POST http://localhost:5000/webhook/deploy -d '{"branch": "main"}'
```

## Project Structure

- `app/`: Main application code.
- `handlers/`: Action handlers for scripts and APIs.
- `tests/`: Verification scripts.
- `config.yaml`: Configuration file.
