import smtplib
from email.mime.text import MIMEText
from app.core.config import settings
from app.core.logging import logger

class EmailAdapter:
    def send_email(self, to_email: str, subject: str, body: str):
        if settings.TEST_MODE or not settings.SMTP_URL:
            logger.info(f"[TEST MODE] Email to {to_email} | Subject: {subject} | Body: {body}")
            with open("/tmp/outgoing_emails.txt", "a") as f: # This might fail on windows if /tmp doesn't exist, handle strictly
                pass 
            return True
            
        try:
            # Parse SMTP URL to get host, port, user, pass
            # msg = MIMEText(body)
            # msg['Subject'] = subject
            # msg['From'] = "ops@copilot.com"
            # msg['To'] = to_email
            # with smtplib.SMTP(...) as server: server.send_message(msg)
            logger.info("Sent real email (mocked implementation)")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

email_adapter = EmailAdapter()
