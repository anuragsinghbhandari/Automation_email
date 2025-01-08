from flask import Blueprint, redirect, url_for, session, request, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from ..config import CLIENT_SECRETS_FILE, SCOPES
import os
import json

auth_bp = Blueprint('auth', __name__)

def credentials_to_dict(credentials):
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
            prompt='consent'
        )
        session['state'] = state
        session.modified = True
        return jsonify({'url': authorization_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/oauth2callback')
def oauth2callback():
    try:
        state = session.get('state')
        if not state:
            return redirect('https://automation-email.vercel.app?auth=error&message=Invalid state')

        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=state,
            redirect_uri=url_for('auth.oauth2callback', _external=True)
        )
        
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        # Store credentials in session
        session['credentials'] = credentials_to_dict(credentials)
        session['authenticated'] = True
        session.modified = True

        # Save credentials to file (optional, for backup)
        try:
            with open('token.json', 'w') as token:
                json.dump(credentials_to_dict(credentials), token)
        except Exception:
            pass  # Ignore file saving errors
            
        return redirect('https://automation-email.vercel.app?auth=success')
    except Exception as e:
        return redirect(f'https://automation-email.vercel.app?auth=error&message={str(e)}')

@auth_bp.route('/auth/status')
def auth_status():
    print("Session contents:", dict(session))  # Debug line
    is_authenticated = False
    try:
        if 'credentials' in session and 'authenticated' in session:
            credentials = Credentials(**session['credentials'])
            is_authenticated = credentials.valid and session['authenticated']
    except Exception as e:
        print("Auth status error:", str(e))  # Debug line
        session.pop('credentials', None)
        session.pop('authenticated', None)
        
    return jsonify({
        'isAuthenticated': is_authenticated
    })

@auth_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True})