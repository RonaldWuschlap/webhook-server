import pytest
from adapters.http_client import ApiClientFactory, ApiClient

def test_client_factory_notification_service():
    factory = ApiClientFactory()
    client = factory.get_client('notification_service')
    assert isinstance(client, ApiClient)

def test_client_factory_media_server_refresh():
    factory = ApiClientFactory()
    client = factory.get_client('media_server_refresh')
    assert isinstance(client, ApiClient)
import pytest
from adapters.http_client import ApiClientFactory, ApiClient

def test_client_factory_notification_service():
    factory = ApiClientFactory()
    client = factory.get_client('notification_service')
    assert isinstance(client, ApiClient)

def test_client_factory_media_server_refresh():
    factory = ApiClientFactory()
    client = factory.get_client('media_server_refresh')
    assert isinstance(client, ApiClient)

def test_client_factory_invalid_client():
    factory = ApiClientFactory()
    client = factory.get_client('invalid_client')
    assert client is None

def test_api_client_send_request_with_headers():
    from unittest.mock import patch, MagicMock
    
    factory = ApiClientFactory()
    client = factory.get_client('media_server_refresh')
    # Check initial headers from config
    assert len(client.headers) == 2
    assert 'Authorization' in client.headers
    assert 'Content-Type' in client.headers
    
    # Mock the requests.request call
    with patch('adapters.http_client.requests.request') as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Send request with additional headers
        response, status_code = client.send_request(headers={'X-Custom-Header': 'test_value'})
        
        # Verify the request was called with merged headers
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        
        # Check that merged headers contain both original and new headers
        merged_headers = call_args.kwargs['headers']
        assert 'Authorization' in merged_headers
        assert 'Content-Type' in merged_headers
        assert 'X-Custom-Header' in merged_headers
        assert merged_headers['X-Custom-Header'] == 'test_value'
        
        # Client headers should not be mutated
        assert len(client.headers) == 2
        assert 'X-Custom-Header' not in client.headers

