from flask import Flask, send_from_directory, session
from flask_cors import CORS
from backend.routes.auth import auth_bp
from backend.routes.automation import automation_bp
from backend.config import FlaskConfig
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
app.config.from_object(FlaskConfig)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://automation-email.vercel.app"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Access-Control-Allow-Origin"],
        "supports_credentials": True
    }
})

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',
    SESSION_COOKIE_NAME='automation_session',
    PERMANENT_SESSION_LIFETIME=1800
)

@app.before_request
def before_request():
    session.permanent = True

# Register blueprints with url prefix
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(automation_bp, url_prefix='/automation')

# Add a route to check if the server is running
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True)
