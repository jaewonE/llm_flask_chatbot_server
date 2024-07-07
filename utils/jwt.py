import time
from flask import g, request, jsonify
from functools import wraps
import time
import jwt
from typing import Dict, Optional, Any
from utils.env import env


class JWT():
    def __init__(self):
        self.JWT_SECRET = env.get("JWT_SECRET")
        self.JWT_ALGORITHM = env.get("JWT_ALGORITHM")
        self.JWT_EXPIRE_TIME = int(env.get("JWT_EXPIRE_TIME"))

    def signJWT(self, payload: Dict[str, Any]) -> str:
        return jwt.encode(payload, self.JWT_SECRET,
                          algorithm=self.JWT_ALGORITHM)

    def sign_user(self, user_name: str) -> str:
        payload = {
            "user_name": user_name,
            "expires": time.time() + self.JWT_EXPIRE_TIME
        }
        return self.signJWT(payload)

    def decodeJWT(self, token: str) -> dict:
        try:
            decoded_token = jwt.decode(
                token, self.JWT_SECRET, algorithms=[self.JWT_ALGORITHM])
            return decoded_token if decoded_token["expires"] >= time.time() else {}
        except:
            return {}

    def verify_user(self, jwt_token: str) -> Optional[str]:
        decoded_token = self.decodeJWT(jwt_token)
        return decoded_token.get("user_name") if "user_name" in decoded_token else None


jwt_instance = JWT()


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if token is None:
            return jsonify({'status': 'error', 'message': 'JWT Token is missing!'}), 401

        # Remove 'Bearer ' from token
        token = token.split(" ")[1] if " " in token else token
        user_name = jwt_instance.verify_user(token)
        if not user_name:
            return jsonify({'status': 'error', 'message': 'Invalid or expired token!'}), 401

        g.user_name = user_name
        return f(*args, **kwargs)
    return decorated_function
