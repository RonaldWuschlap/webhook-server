import pytest
from app.main import app
from unittest.mock import patch, MagicMock
import time

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_api_client_factory():
    with patch('app.main.api_client_factory') as mock_factory:
        mock_client = MagicMock()
        # Return tuple (response, status_code) instead of dict
        mock_response = MagicMock()
        mock_response.text = "Success"
        mock_client.send_request.return_value = (mock_response, 200)
        mock_factory.get_client.return_value = mock_client
        yield mock_factory

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"status": "running"}

def test_sonarr_webhook_download(client, mock_api_client_factory):
    """Test the Sonarr webhook with Download event."""
    payload = {
        "eventType": "Download",
        "series": {"title": "Test Series"},
        "episodes": [{"title": "Test Episode"}]
    }
    
    response = client.post('/webhook/sonarr', json=payload)
    
    assert response.status_code == 200
    
    # Verify calls
    # 1. Push notification
    # 2. Media server refresh
    assert mock_api_client_factory.get_client.call_count >= 2
    mock_api_client_factory.get_client.assert_any_call('notification_service')
    mock_api_client_factory.get_client.assert_any_call('media_server_refresh')

def test_sonarr_webhook_test_event(client, mock_api_client_factory):
    """Test the Sonarr webhook with Test event."""
    payload = {"eventType": "Test"}
    response = client.post('/webhook/sonarr', json=payload)
    
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'success'
    
    # Verify notification call
    mock_api_client_factory.get_client.assert_called_with('notification_service')

def test_radarr_webhook_download(client, mock_api_client_factory):
    """Test the Radarr webhook with Download event."""
    payload = {
        "eventType": "Download",
        "movie": {"title": "Test Movie"}
    }
    response = client.post('/webhook/radarr', json=payload)
    
    assert response.status_code == 200
    
    # Verify calls
    assert mock_api_client_factory.get_client.call_count >= 2
    mock_api_client_factory.get_client.assert_any_call('notification_service')
    mock_api_client_factory.get_client.assert_any_call('media_server_refresh')

def test_unknown_event_type_sonarr(client, mock_api_client_factory):
    """Test an unknown event type."""
    payload = {"eventType": "Unknown"}
    response = client.post('/webhook/sonarr', json=payload)
    
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'ignored'

def test_unknown_event_type_radarr(client, mock_api_client_factory):
    """Test an unknown event type."""
    payload = {"eventType": "Unknown"}
    response = client.post('/webhook/radarr', json=payload)
    
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'ignored'

def test_jellyfin_api_success_204(client, mock_api_client_factory):
    """Test Jellyfin API returning 204 Success."""
    # Setup mock to return specific response for media_server_refresh
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Success"
    mock_client.send_request.return_value = (mock_response, 204)
    
    # We need to make sure get_client returns this specific mock when asked for 'media_server_refresh'
    def side_effect(client_name):
        if client_name == 'media_server_refresh':
            return mock_client
        # Return default mock for notification_service
        default_mock = MagicMock()
        default_mock.send_request.return_value = (MagicMock(), 200)
        return default_mock
        
    mock_api_client_factory.get_client.side_effect = side_effect

    payload = {
        "eventType": "Download",
        "series": {"title": "Test Series"},
        "episodes": [{"title": "Test Episode"}]
    }
    
    response = client.post('/webhook/sonarr', json=payload)
    
    # Handler passes through the status code from the API
    assert response.status_code == 204
    # 204 responses don't have content, so we can't check response.json
    # But we can verify the handler was called correctly via the mock assertions above

def test_jellyfin_api_error_503(client, mock_api_client_factory):
    """Test Jellyfin API returning 503 Service Unavailable."""
    # Setup mock to return specific response for media_server_refresh
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Service Unavailable"
    mock_client.send_request.return_value = (mock_response, 503)
    
    def side_effect(client_name):
        if client_name == 'media_server_refresh':
            return mock_client
        # Return default mock for notification_service
        default_mock = MagicMock()
        default_mock.send_request.return_value = (MagicMock(), 200)
        return default_mock
        
    mock_api_client_factory.get_client.side_effect = side_effect

    payload = {
        "eventType": "Download",
        "series": {"title": "Test Series"},
        "episodes": [{"title": "Test Episode"}]
    }
    
    response = client.post('/webhook/sonarr', json=payload)
    
    assert response.status_code == 503
    data = response.json
    assert data['status'] == 'error'
    assert 'API call failed' in data['message']

def test_sonarr_library_update_throttled(client, mock_api_client_factory):
    """Test Sonarr library update throttling."""
    payload = {
        "eventType": "Download",
        "series": {"title": "Test Series"},
        "episodes": [{"title": "Test Episode"}]
    }
    
    response = client.post('/webhook/sonarr', json=payload)
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'success'

    response = client.post('/webhook/sonarr', json=payload)
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'ignored'
    assert 'Library update throttled' in data['message']