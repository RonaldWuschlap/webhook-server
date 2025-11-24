import yaml
from flask import Flask, request, jsonify
import logging
import sys
import os

# Add parent directory to path to allow importing handlers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handlers.actions import HANDLERS
from adapters.http_client import ApiClientFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()
api_client_factory = ApiClientFactory()

from flask import Response

def create_endpoint_handler(handler_func, target_api):
    def handler():
        payload = request.json
        result = handler_func(payload, api_client_factory, target_api)

        status_code = 200
        if isinstance(result, tuple) and len(result) == 2:
            result, status_code = result

        try:
            return jsonify(result), status_code
        except TypeError:
            # Fallback for non-json serializable results
            return Response(str(result), status=status_code)
    return handler

# Register routes from config
if 'webhooks' in config:
    for webhook_name, webhook_config in config['webhooks'].items():
        path = webhook_config.get('path')
        handler_name = webhook_config.get('handler')
        target_api = webhook_config.get('target_api')
        
        if path and handler_name:
            if handler_name in HANDLERS:
                handler_func = HANDLERS[handler_name]
                endpoint_name = f"handler_{path.replace('/', '_')}"
                app.add_url_rule(path, endpoint_name, create_endpoint_handler(handler_func, target_api), methods=['POST'])
                logger.info(f"Registered endpoint: {path} -> {handler_name}")
            else:
                logger.error(f"Handler '{handler_name}' not found for path {path}")

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "running"}), 200

if __name__ == '__main__':
    server_config = config.get('server', {})
    port = server_config.get('port', 5000)
    app.run(host='0.0.0.0', port=port)
