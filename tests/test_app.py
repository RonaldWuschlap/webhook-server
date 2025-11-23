import pytest
from app.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"status": "running"}

def test_deploy_webhook(client):
    """Test the deploy webhook endpoint."""
    payload = {"branch": "main"}
    response = client.post('/webhook/deploy', json=payload)
    
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'received'
    assert len(data['results']) == 1
    assert data['results'][0]['status'] == 'success'
    # We expect the echo command to run successfully
    assert "Deploying..." in data['results'][0]['output']

def test_notify_webhook(client):
    """Test the notify webhook endpoint."""
    payload = {"event": "test_event"}
    response = client.post('/webhook/notify', json=payload)
    
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'received'
    assert len(data['results']) == 1
    # Note: This actually makes a network call to httpbin.org unless mocked.
    # For a unit test, we might want to mock this, but for now we test the integration
    # as per previous tests.
    assert data['results'][0]['status'] == 'success'
    assert data['results'][0]['status_code'] == 200
