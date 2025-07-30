"""
Standard OAuth2 implementation
"""
import requests
import base64
import time
import json
from typing import Dict, Any

class OAuth2Manager:
    def __init__(self, client_id: str, client_secret: str, token_url: str, 
                 auth_url: str = None, redirect_uri: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.auth_url = auth_url
        self.redirect_uri = redirect_uri
        self._cached_token = None
        self._token_expires_at = None
    
    # ... (keep all the existing OAuth2Manager methods from before)