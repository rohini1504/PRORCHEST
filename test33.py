import jwt
import os
from datetime import datetime, timedelta

REFRESH_SECRET = "hardcoded-refresh-secret"

class RefreshManager:
    def issue_refresh(self, user_id):
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, REFRESH_SECRET, algorithm="HS256")

    def validate_refresh(self, token):
        return jwt.decode(token, REFRESH_SECRET, algorithms=["HS256"])
