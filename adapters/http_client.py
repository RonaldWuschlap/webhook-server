import requests
import logging

logger = logging.getLogger(__name__)

class ApiClient:
    """
    A configured HTTP client for making API calls.
    """
    def __init__(self, config):
        self.url = config.get('url')
        self.method = config.get('method', 'GET')
        self.headers = config.get('headers', {})

    def send_request(self, headers=None, payload=None) -> tuple[requests.Response | None, int]:
        """
        Makes an external API call using the configured settings.
        
        Args:
            headers (dict, optional): Additional headers to merge with configured headers.
            payload (dict, optional): Data to send in the request body.
            
        Returns:
            tuple: (response, status_code) or (None, 500) on error.
        """
        try:
            # Use provided payload or empty dict
            data = payload if payload else {}
            
            # Merge headers - dict.update() returns None, so we need to create a new dict
            merged_headers = self.headers.copy()
            if headers:
                merged_headers.update(headers)
            
            logger.info(f"Making API call to {self.url} with method {self.method}")
            response = requests.request(self.method, self.url, headers=merged_headers, json=data)
            logger.info(f"API response status: {response.status_code}")
            
            return response, response.status_code
        except Exception as e:
            logger.error(f"Failed to make API call: {e}")
            return None, 500

import yaml

class ApiClientFactory:
    """
    Factory for creating configured ApiClient instances.
    """
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)

    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                full_config = yaml.safe_load(f)
                return full_config.get('api_clients', {})
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            return {}

    def get_client(self, client_name):
        """
        Returns an ApiClient instance for the given client name.
        
        Args:
            client_name (str): The name of the API client in the configuration.
            
        Returns:
            ApiClient: A configured ApiClient instance, or None if not found.
        """
        if client_name in self.config:
            return ApiClient(self.config[client_name])
        else:
            logger.warning(f"API client configuration '{client_name}' not found")
            return None
