from flask import Flask, send_from_directory, session
from flask_cors import CORS
from backend.routes.auth import auth_bp
from backend.routes.automation import automation_bp
from backend.config import FlaskConfig
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')
app.config.from_object(FlaskConfig)
# Configure CORS with specific settings
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Access-Control-Allow-Origin"],
        "supports_credentials": True
    }
})

# Configure session
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
)


# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(automation_bp)

@app.route('/')
def index():
    print("back")
    return send_from_directory('frontend/dist', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)