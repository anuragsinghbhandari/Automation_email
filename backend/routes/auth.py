from flask import Blueprint, redirect, url_for, session, request, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from ..config import CLIENT_SECRETS_FILE, SCOPES
import os
import json

auth_bp = Blueprint('auth', __name__)

def credentials_to_dict(credentials):
    """Convert credentials to a dictionary."""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

@auth_bp.route('/login')
def login():
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=url_for('auth.oauth2callback', _external=True)
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to ensure refresh token
        )
        session['state'] = state
        session.modified = True
        return redirect(authorization_url)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/oauth2callback')
def oauth2callback():
    try:
        if 'state' not in session:
            return redirect('http://automation-email.vercel.app?auth=error&message=Invalid state')

        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=session['state'],
            redirect_uri=url_for('auth.oauth2callback', _external=True)
        )
        
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        # Store credentials in session
        session['credentials'] = credentials_to_dict(credentials)
        session.modified = True

        # Save credentials to file
        with open('token.json', 'w') as token:
            json.dump(credentials_to_dict(credentials), token)
            
        return redirect('http://automation-email.vercel.app?auth=success')
    except Exception as e:
        return redirect(f'http://automation-email.vercel.app?auth=error&message={str(e)}')

@auth_bp.route('/auth/status')
def auth_status():
    is_authenticated = False
    try:
        if 'credentials' in session:
            credentials = Credentials(**session['credentials'])
            is_authenticated = credentials.valid
    except Exception:
        session.pop('credentials', None)
        
    return jsonify({
        'isAuthenticated': is_authenticated
    })

@auth_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True})