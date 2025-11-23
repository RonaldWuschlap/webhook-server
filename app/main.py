import yaml
from flask import Flask, request, jsonify
import logging
from handlers.actions import execute_script, make_api_call

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

def create_endpoint_handler(actions):
    def handler():
        payload = request.json
        results = []
        for action in actions:
            action_type = action.get('type')
            if action_type == 'script':
                command = action.get('command')
                result = execute_script(command, payload)
                results.append(result)
            elif action_type == 'api':
                url = action.get('url')
                method = action.get('method', 'GET')
                headers = action.get('headers', {})
                # Use configured payload if present, otherwise forward webhook payload
                api_payload = action.get('payload', payload) 
                result = make_api_call(url, method, headers, payload=api_payload)
                results.append(result)
            else:
                logger.warning(f"Unknown action type: {action_type}")
        
        return jsonify({"status": "received", "results": results}), 200
    return handler

# Register routes from config
if 'endpoints' in config:
    for endpoint in config['endpoints']:
        path = endpoint.get('path')
        methods = [endpoint.get('method', 'POST')]
        actions = endpoint.get('actions', [])
        
        if path:
            endpoint_name = f"handler_{path.replace('/', '_')}"
            app.add_url_rule(path, endpoint_name, create_endpoint_handler(actions), methods=methods)
            logger.info(f"Registered endpoint: {path} [{methods}]")

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "running"}), 200

if __name__ == '__main__':
    port = config.get('port', 5000)
    app.run(host='0.0.0.0', port=port)
