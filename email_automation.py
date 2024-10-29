import sys
import imaplib
import email
from email.header import decode_header
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import time
import random
from email.utils import parsedate_to_datetime
from imapclient import IMAPClient
from email.message import EmailMessage
import pytz
import logging

# Add at the top of your file
import sys
import os

# Modify the logging configuration
log_directory = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_directory, 'email_automation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Email account credentials from environment variables
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
SMTP_SERVER = os.getenv("SMTP_SERVER")
#SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_PORT = 587
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate environment variables
required_env_vars = ["EMAIL", "EMAIL_PASSWORD", "IMAP_SERVER", "SMTP_SERVER", "GROQ_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Set up the Groq LLM
llm = ChatGroq(
    model_name="llama-3.1-70b-versatile",
    temperature=0.7,
    max_tokens=500,
    top_p=1
)

# Enhanced prompt template
prompt_template = PromptTemplate(
    input_variables=["client", "body"],
    template="""
    Client: {client}
    Email Content: {body}

    Generate a professional and empathetic reply as Anurag Singh Bhandari, a 20-year-old entrepreneur from Khora, U.P, India.
    
    Guidelines:
    - Address the main points concisely
    - Maintain a professional yet friendly tone
    - Keep the response clear and focused
    - Include a polite greeting and sign-off
    
    Reply:
    """
)

chain = LLMChain(llm=llm, prompt=prompt_template)

def clean_email_content(content: str) -> str:
    """Clean and format email content by removing HTML, URLs, and extra whitespace."""
    if not content:
        return "No content available"
    
    try:
        # Remove HTML tags
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator=' ')

        # Remove URLs and email addresses
        text = re.sub(r'http[s]?://\S+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', text)

        # Clean up whitespace
        text = ' '.join(text.split())
        
        # Truncate with ellipsis if too long
        max_length = 1000
        return text[:max_length] + '...' if len(text) > max_length else text
    except Exception as e:
        logger.error(f"Error cleaning email content: {e}")
        return "Error processing email content"

def generate_reply(client: str, body: str) -> str:
    """Generate a reply using the LLM chain with error handling."""
    try:
        return chain.run(client=client, body=body)
    except Exception as e:
        logger.error(f"Error generating reply: {e}")
        return "I apologize, but I am currently unable to generate a response. Please try again later."

def send_reply(to_email: str, body: str) -> bool:
    """Send email reply with enhanced error handling and retry logic."""
    msg = EmailMessage()
    msg['From'] = EMAIL
    msg['To'] = to_email
    msg['Subject'] = 'Re: ' # Adding 'Re:' prefix for better email threading
    msg.set_content(body)
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                server.starttls()
                server.login(EMAIL, PASSWORD)
                server.send_message(msg)
            logger.info(f"Reply sent successfully to: {to_email}")
            return True
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"Failed to send reply to {to_email} after {max_retries} attempts")
                return False

def get_email_body(msg: EmailMessage) -> str:
    """Extract email body with improved handling of different content types."""
    try:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8', errors='replace')
                elif part.get_content_type() == "text/html":
                    # Fall back to HTML if no plain text is found
                    return part.get_payload(decode=True).decode('utf-8', errors='replace')
        else:
            return msg.get_payload(decode=True).decode('utf-8', errors='replace')
    except Exception as e:
        logger.error(f"Error extracting email body: {e}")
        return None

def process_email(client: IMAPClient, msg_id: int) -> bool:
    """Process a single email with improved error handling and logging."""
    try:
        email_data = client.fetch([msg_id], ['RFC822', 'INTERNALDATE'])
        if msg_id not in email_data:
            logger.error(f"Failed to fetch email with ID {msg_id}")
            return False
        
        msg_data = email_data[msg_id]
        email_message = email.message_from_bytes(msg_data[b'RFC822'])
        
        # Extract and decode subject
        subject = decode_header(email_message["Subject"])[0][0]
        subject = subject.decode() if isinstance(subject, bytes) else str(subject)
        
        sender = email_message.get("From")
        sender_name = extract_sender_name(sender)
        
        logger.info(f"Processing email: Subject='{subject}', From={sender}")
        
        body = get_email_body(email_message)
        if not body:
            logger.warning(f"No readable content in email ID {msg_id}")
            return False
            
        cleaned_body = clean_email_content(body)
        reply_body = generate_reply(sender_name, cleaned_body)
        
        if send_reply(sender, reply_body):
            client.add_flags(msg_id, [b'\\Seen'])
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error processing email {msg_id}: {e}")
        return False

def extract_sender_name(sender: str) -> str:
    """Extract sender's name from email address."""
    if '<' in sender:
        name = sender.split('<')[0].strip()
        return name.strip('" ')  # Remove quotes if present
    return sender.split('@')[0]  # Fallback to using part before @ if no name found

def listen_for_emails():
    """Main email listening loop with improved connection handling and monitoring."""
    logger.info("Starting email monitoring service...")
    
    reconnect_delay = 5  # Initial delay in seconds
    max_reconnect_delay = 300  # Maximum delay (5 minutes)
    
    while True:
        try:
            with IMAPClient(IMAP_SERVER, use_uid=True, ssl=True) as client:
                client.login(EMAIL, PASSWORD)
                client.select_folder('INBOX')
                logger.info("Connected to IMAP server")
                
                # Get initial state
                initial_messages = client.search(['ALL'])
                last_seen_id = max(initial_messages) if initial_messages else 0
                logger.info(f"Starting monitoring from message ID: {last_seen_id}")
                
                # Reset reconnect delay after successful connection
                reconnect_delay = 5
                
                while True:
                    try:
                        client.idle()
                        logger.info("Waiting for new emails...")
                        responses = client.idle_check(timeout=30)
                        
                        if responses:
                            client.idle_done()
                            new_messages = client.search(['UNSEEN'])
                            new_messages = [msg_id for msg_id in new_messages if msg_id > last_seen_id]
                            
                            if new_messages:
                                logger.info(f"Processing {len(new_messages)} new messages")
                                for msg_id in new_messages:
                                    if process_email(client, msg_id):
                                        last_seen_id = max(last_seen_id, msg_id)
                        else:
                            client.idle_done()
                            
                    except (ConnectionError, TimeoutError) as e:
                        raise e  # Re-raise to trigger reconnection
                        
        except Exception as e:
            logger.error(f"Connection error: {e}")
            logger.info(f"Reconnecting in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)

if __name__ == "__main__":
    try:
        listen_for_emails()
    except KeyboardInterrupt:
        logger.info("Email monitoring service stopped by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
