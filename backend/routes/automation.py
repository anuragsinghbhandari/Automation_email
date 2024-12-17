from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from ..services.gmail_service import GmailService
from ..services.llm_service import LLMService
from ..services.knowledge_service import KnowledgeService
from ..config import FlaskConfig
from ..routes.auth import session
import json
import logging
import threading
import time

logger = logging.getLogger(__name__)

automation_bp = Blueprint('automation', __name__)
llm_service = LLMService()
knowledge_service = KnowledgeService(llm_service.llm)

# Global variables to store email details
email_details = {
    'received': None,
    'sent': None
}

@automation_bp.route('/start', methods=['POST'])
def start_automation():
    if 'pdfs' in request.files:
        files = request.files.getlist('pdfs')
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(FlaskConfig.UPLOAD_FOLDER, filename))

    knowledge_service.initialize_knowledge_base()

    with open('token.json', 'r') as token:
        data = json.load(token)

    response = jsonify({'message': 'Automation started successfully'})
    response.status_code = 200

    def email_monitoring():
        gmail_service = GmailService.build_service(data)
        results = gmail_service.users().messages().list(userId='me', maxResults=1).execute()
        messages = results.get('messages', [])
        latest_message_id = messages[0]['id']

        while True:
            unread_messages_id = GmailService.get_unread_messageid(gmail_service, latest_message_id)
            email_data = gmail_service.users().messages().get(userId='me', id=unread_messages_id).execute()
            payload = email_data.get('payload', {})
            headers = payload.get('headers', [])

            subject = next(header['value'] for header in headers if header['name'] == 'Subject')
            sender = next(header['value'] for header in headers if header['name'] == 'From')

            logger.info(f"Processing email: Subject='{subject}', From={sender}")

            body = email_data['snippet']
            context = knowledge_service.get_relevant_context(body)
            reply = llm_service.generate_reply(sender, body, context)

            GmailService.send_email(gmail_service, sender, subject, reply)

            # Update global email details
            email_details['received'] = f"Email Received: {subject} from {sender} at {time.strftime('%d-%m-%Y %H:%M:%S',time.localtime())}"
            email_details['sent'] = f"Email Sent: {subject} to {sender} at {time.strftime('%d-%m-%Y %H:%M:%S',time.localtime())}"

            latest_message_id = unread_messages_id
            time.sleep(5)  # Polling interval

    thread = threading.Thread(target=email_monitoring)
    thread.start()

    return response

@automation_bp.route('/email-status', methods=['GET'])
def get_email_status():
    return jsonify(email_details)
