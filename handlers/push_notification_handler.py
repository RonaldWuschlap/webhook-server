import logging
from handlers.constants import allowed_event_types

logger = logging.getLogger(__name__)

def handle_push_notification(payload, api_client_factory, target_api_name='notification_service'):
    """
    Handles webhooks by sending push notifications via ntfy.
    """
    logger.info("Received webhook for push notification")

    event_type = payload.get('eventType')
    logger.info(f"Event Type: {event_type}")

    if event_type not in allowed_event_types:
        logger.warning(f"Event type '{event_type}' not allowed")
        return {"status": "ignored", "message": "Event type ignored"}, 200

    # Dispatch to specific builder
    notification_result = _build_notification(event_type, payload)
    
    if not notification_result:
        logger.warning(f"No notification built for event type '{event_type}'")
        return {"status": "ignored", "message": "No notification content"}, 200

    # Unpack data and headers
    notification_data, notification_headers = notification_result

    # Send notification
    client = api_client_factory.get_client(target_api_name)
    if not client:
        logger.warning(f"Target API '{target_api_name}' not found in configuration")
        return {"status": "error", "message": "Target API configuration missing"}, 500
    
    response, status_code = client.send_request(headers=notification_headers, payload=notification_data)
    
    # Handle error responses
    if response is None:
        logger.error("Failed to send push notification: Connection error")
        return {"status": "error", "message": "Notification send failed"}, status_code
    
    if status_code >= 400:
        error_message = response.text or "Unknown error sending notification"
        logger.error(f"Failed to send push notification: {error_message}")
        return {"status": "error", "message": f"Notification send failed: {error_message}"}, status_code
    
    # Success response
    logger.info("Successfully sent push notification")
    return {"status": "success", "message": "Notification sent"}, status_code

def _build_notification(event_type, payload):
    """
    Dispatches to the appropriate notification builder based on event type.
    """
    builders = {
        'Download': _build_download_notification,
        'Test': _build_test_notification,
        'Grab': _build_grab_notification,
        'Health': _build_health_notification,
        'ApplicationUpdate': _build_application_update_notification,
        'HealthRestored': _build_health_restored_notification,
        'ManualInteractionRequired': _build_manual_interaction_notification
    }
    
    builder = builders.get(event_type)
    if builder:
        return builder(payload)
    return None

def _build_download_notification(payload):
    # Extract title from either series (Sonarr) or movie (Radarr)
    title = payload.get('series', {}).get('title') or payload.get('movie', {}).get('title', 'Unknown')
    data = f"A download has been completed for {title}"
    headers = {
        "Title": "Download Completed",
        "Priority": "default",
        "Tags": "download"
    }
    return data, headers

def _build_test_notification(payload):
    # Test events may not have series/movie info
    title = payload.get('series', {}).get('title') or payload.get('movie', {}).get('title', 'webhook')
    data = f"This is a test notification for {title}"
    headers = {
        "Title": "Test Notification",
        "Priority": "low",
        "Tags": "test"
    }
    return data, headers

def _build_grab_notification(payload):
    # Extract title from either series (Sonarr) or movie (Radarr)
    title = payload.get('series', {}).get('title') or payload.get('movie', {}).get('title', 'Unknown')
    data = f"Content has been grabbed for {title}"
    headers = {
        "Title": "Grabbed",
        "Priority": "default",
        "Tags": "grab"
    }
    return data, headers

def _build_health_notification(payload):
    # TODO: Implement Health notification structure
    data = "A health issue was detected."
    headers = {
        "Title": "Health Issue",
        "Priority": "high",
        "Tags": "health,warning"
    }
    return data, headers

def _build_application_update_notification(payload):
    # TODO: Implement ApplicationUpdate notification structure
    data = "The application has been updated."
    headers = {
        "Title": "Application Updated",
        "Priority": "low",
        "Tags": "update"
    }
    return data, headers

def _build_health_restored_notification(payload):
    # TODO: Implement HealthRestored notification structure
    data = "Health issues have been resolved."
    headers = {
        "Title": "Health Restored",
        "Priority": "default",
        "Tags": "health,success"
    }
    return data, headers

def _build_manual_interaction_notification(payload):
    # TODO: Implement ManualInteractionRequired notification structure
    data = "User intervention is required."
    headers = {
        "Title": "Manual Interaction Required",
        "Priority": "high",
        "Tags": "manual,alert"
    }
    return data, headers
