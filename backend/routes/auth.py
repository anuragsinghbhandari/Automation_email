from flask import Blueprint, redirect, url_for, session, request, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from ..config import CLIENT_SECRETS_FILE, SCOPES
import os
import json
import secrets

# Create blueprint without url_prefix - we'll handle paths in the routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    try:
        # Generate a secure state token
        state = secrets.token_urlsafe(32)
        
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=url_for('auth.oauth2callback', _external=True)
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=state
        )

        session['oauth_state'] = state
        session.modified = True
        
        return jsonify({'url': authorization_url})
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/oauth2callback')
def oauth2callback():
    try:
        stored_state = session.get('oauth_state')
        received_state = request.args.get('state')

        if not stored_state or stored_state != received_state:
            return redirect('https://automation-email.vercel.app?auth=error&message=Invalid state')

        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=received_state,
            redirect_uri=url_for('auth.oauth2callback', _external=True)
        )
        
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        session['credentials'] = credentials_to_dict(credentials)
        session.modified = True
        session.pop('oauth_state', None)
            
        return redirect('https://automation-email.vercel.app?auth=success')
    except Exception as e:
        print(f"Callback error: {str(e)}")
        return redirect(f'https://automation-email.vercel.app?auth=error&message={str(e)}')

# Changed from /auth/status to /status
@auth_bp.route('/status')
def auth_status():
    print("Status endpoint called")  # Debug log
    is_authenticated = False
    try:
        if 'credentials' in session:
            credentials = Credentials(**session['credentials'])
            is_authenticated = credentials.valid
    except Exception as e:
        print(f"Auth status error: {str(e)}")
        session.pop('credentials', None)
        
    return jsonify({
        'isAuthenticated': is_authenticated
    })

@auth_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
