from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
import logging
from ..config import SCOPES

logger = logging.getLogger(__name__)


class GmailService:
    
    @staticmethod
    def build_service(credentials_dict):
        credentials = Credentials(**credentials_dict)
        return build('gmail', 'v1', credentials=credentials)

    @staticmethod
    def send_email(service, to_email, subject, body):
        try:
            message = {
                'raw': base64.urlsafe_b64encode(
                    f'To: {to_email}\nSubject: {subject}\n\n{body}'.encode()
                ).decode()
            }
            service.users().messages().send(userId='me', body=message).execute()
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    @staticmethod
    def get_unread_messageid(service, latest_id):
        while True:
            try:
                # Fetch unread messages
                results = service.users().messages().list(userId='me', q='is:unread').execute()
                messages = results.get('messages', [])
                for msg in messages:
                    msg_id = msg['id']
                    
                    # Only process new messages (those with IDs greater than the last processed ID)
                    if msg_id > latest_id:
                        return msg_id           
            except Exception as e:
                logger.error(f"Error fetching unread messages: {e}")
                return []
