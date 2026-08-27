import requests
from app.core.config import settings
from app.core.logging import logger

class SlackAdapter:
    def send_message(self, channel: str, text: str):
        if settings.TEST_MODE or not settings.SLACK_WEBHOOK_URL:
            logger.info(f"[TEST MODE] Slack Message to {channel}: {text}")
            return True
            
        payload = {"text": text, "channel": channel}
        try:
            resp = requests.post(settings.SLACK_WEBHOOK_URL, json=payload)
            resp.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False

slack_adapter = SlackAdapter()
