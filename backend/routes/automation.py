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

logger = logging.getLogger(__name__)

automation_bp = Blueprint('automation', __name__)
llm_service = LLMService()
knowledge_service = KnowledgeService(llm_service.llm)

@automation_bp.route('/start', methods=['POST'])
def start_automation():
    if 'pdfs' in request.files:
        files = request.files.getlist('pdfs')
        for file in files:
            if file.filename:
                print(file.filename)
                filename = secure_filename(file.filename)
                file.save(os.path.join(FlaskConfig.UPLOAD_FOLDER, filename))
    print(1)
    Knowlegde = knowledge_service.initialize_knowledge_base()

    print(2)
    with open('token.json', 'r') as token:
            data = json.load(token)
    print("Starting Email Monitoring")
    # New logic to read unseen emails
    gmail_service = GmailService.build_service(data)  # Assuming credentials are stored in session

    results = gmail_service.users().messages().list(userId='me', maxResults=1).execute()
    messages = results.get('messages', [])
    # Extract the message ID of the latest email
    latest_message_id = messages[0]['id']

    while True:
        unread_messages_id = GmailService.get_unread_messageid(gmail_service,latest_message_id)
        email_data = gmail_service.users().messages().get(userId='me',id= unread_messages_id).execute()
        print(f"Email Recieved id: {unread_messages_id}")
        payload = email_data.get('payload',{})
        headers = payload.get('headers',[])
        
        # Extract subject and sender
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        sender = next(header['value'] for header in headers if header['name'] == 'From')
        
        logger.info(f"Processing email: Subject='{subject}', From={sender}")
        
        # Get the email body
        body = email_data['snippet']  # Use snippet for a quick response
        
        # Get relevant context from knowledge service
        context = knowledge_service.get_relevant_context(body)

        # Generate a reply using LLM service
        reply = llm_service.generate_reply(sender, body, context)

        # Send the reply
        GmailService.send_email(gmail_service, sender, subject, reply)
        latest_message_id = unread_messages_id
        print(f"email sent id: {unread_messages_id}")
    return jsonify({'message': 'Automation started successfully'})
