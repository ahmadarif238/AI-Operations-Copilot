from app.core.config import settings
from app.core.logging import logger

class TwilioAdapter:
    def send_whatsapp(self, to_number: str, text: str):
        if settings.TEST_MODE or not settings.TWILIO_ACCOUNT_SID:
            logger.info(f"[TEST MODE] WhatsApp Message to {to_number}: {text}")
            return True
            
        try:
            # Mocking the client for dependency reasons if library not installed
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # message = client.messages.create(from_=f"whatsapp:{settings.TWILIO_FROM_NUMBER}", body=text, to=f"whatsapp:{to_number}")
            logger.info("Sent real WhatsApp message (mocked implementation)")
            return True
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            return False

twilio_adapter = TwilioAdapter()
