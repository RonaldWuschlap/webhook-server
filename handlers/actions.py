import subprocess
import requests
import logging

logger = logging.getLogger(__name__)

def execute_script(command, payload=None):
    """
    Executes a shell command.
    """
    try:
        # TODO: Implement variable substitution from payload if needed
        logger.info(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logger.info(f"Command output: {result.stdout}")
        if result.stderr:
            logger.error(f"Command error: {result.stderr}")
        return {"status": "success", "output": result.stdout, "error": result.stderr, "return_code": result.returncode}
    except Exception as e:
        logger.error(f"Failed to execute command: {e}")
        return {"status": "error", "message": str(e)}

def make_api_call(url, method="GET", headers=None, payload=None, data=None):
    """
    Makes an external API call.
    """
    try:
        logger.info(f"Making API call to {url} with method {method}")
        response = requests.request(method, url, headers=headers, json=payload, data=data)
        logger.info(f"API response status: {response.status_code}")
        return {"status": "success", "status_code": response.status_code, "response": response.text}
    except Exception as e:
        logger.error(f"Failed to make API call: {e}")
        return {"status": "error", "message": str(e)}
