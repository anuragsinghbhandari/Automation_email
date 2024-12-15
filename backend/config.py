import os
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()

# OAuth Configuration
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = 'token.json'

# Flask Configuration
class FlaskConfig:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
    UPLOAD_FOLDER = 'knowledge_base'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'