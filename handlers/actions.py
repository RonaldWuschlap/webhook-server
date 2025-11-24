import logging
from handlers.push_notification_handler import handle_push_notification
from handlers.constants import allowed_event_types, trigger_library_events
from adapters.http_client import ApiClientFactory

logger = logging.getLogger(__name__)

def handle_sonarr(payload: dict, api_client_factory: ApiClientFactory, target_api_name: str = 'media_server'):
    """
    Handles Sonarr webhooks.
    """
    logger.info("Received Sonarr webhook")
    
    event_type = payload.get('eventType')
    logger.info(f"Sonarr Event Type: {event_type}")

    if event_type not in allowed_event_types:
        logger.warning(f"Event type '{event_type}' not allowed")
        return {"status": "ignored", "message": "Event type ignored"}, 200

    # Send push notification (ignore result for now)
    handle_push_notification(payload, api_client_factory)

    if event_type == 'Download':
        # Trigger API call
        client = api_client_factory.get_client(target_api_name)
        if not client:
            logger.warning(f"Target API '{target_api_name}' not found in configuration")
            return {"status": "error", "message": "Target API configuration missing"}, 500
        
        response, status_code = client.send_request({})
        
        # Handle error responses
        if response is None:
            logger.error("Failed to trigger library refresh for Sonarr Download event: Connection error")
            return {"status": "error", "message": "API call failed"}, status_code
        
        if status_code >= 400:
            error_message = response.text or "Unknown error during library refresh"
            logger.error(f"Failed to trigger library refresh for Sonarr Download event: {error_message}")
            return {"status": "error", "message": f"API call failed: {error_message}"}, status_code
        
        # Success response
        logger.info(f"Successfully triggered library refresh for Sonarr Download event")
        return {"status": "success", "message": "Library refresh triggered"}, status_code
            
    elif event_type == 'Test':
        logger.info("Received Test event from Sonarr")
        return {"status": "success", "message": "Test event received"}, 200

def handle_radarr(payload: dict, api_client_factory: ApiClientFactory, target_api_name: str = 'media_server'):
    """
    Handles Radarr webhooks.
    """
    logger.info("Received Radarr webhook")

    event_type = payload.get('eventType')
    logger.info(f"Radarr Event Type: {event_type}")

    if event_type not in allowed_event_types:
        logger.warning(f"Event type '{event_type}' not allowed")
        return {"status": "ignored", "message": "Event type ignored"}, 200

    # Send push notification (ignore result for now)
    handle_push_notification(payload, api_client_factory)

    if event_type == 'Download':
        # Trigger API call
        client = api_client_factory.get_client(target_api_name)
        if not client:
            logger.warning(f"Target API '{target_api_name}' not found in configuration")
            return {"status": "error", "message": "Target API configuration missing"}, 500
        
        response, status_code = client.send_request({})
        
        # Handle error responses
        if response is None:
            logger.error("Failed to trigger library refresh for Radarr Download event: Connection error")
            return {"status": "error", "message": "API call failed"}, status_code
        
        if status_code >= 400:
            error_message = response.text or "Unknown error during library refresh"
            logger.error(f"Failed to trigger library refresh for Radarr Download event: {error_message}")
            return {"status": "error", "message": f"API call failed: {error_message}"}, status_code
        
        # Success response
        logger.info(f"Successfully triggered library refresh for Radarr Download event")
        return {"status": "success", "message": "Library refresh triggered"}, status_code

    elif event_type == 'Test':
        logger.info("Received Test event from Radarr")
        return {"status": "success", "message": "Test event received"}, 200

    # Handle other event types
    return {"status": "ignored", "message": f"Event type '{event_type}' ignored"}, 200

# Registry of available handlers
HANDLERS = {
    'sonarr': handle_sonarr,
    'radarr': handle_radarr
}
