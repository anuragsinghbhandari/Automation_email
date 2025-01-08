from flask import Flask, send_from_directory, session
from flask_cors import CORS
from backend.routes.auth import auth_bp
from backend.routes.automation import automation_bp
from backend.config import FlaskConfig
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
app.config.from_object(FlaskConfig)

# Updated CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": ["https://automation-email.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Access-Control-Allow-Origin"],
        "supports_credentials": True
    }
})

# Critical: Update session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',  # Important for cross-site requests
    SESSION_COOKIE_NAME='automation_session',  # Custom session name
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
)

@app.before_request
def before_request():
    session.permanent = True  # Make session permanent
