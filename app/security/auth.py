"""Authentication"""
import logging
from typing import Optional
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AuthHandler:
    """Handle authentication"""
    
    def __init__(self, secret_key: str = "change-me-in-production"):
        self.secret_key = secret_key
    
    def create_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Create JWT token"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

