from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")
SECRET_KEY = os.getenv("SECRET_KEY")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")
            self.validate_token(credentials.credentials)

        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")

    @staticmethod
    def validate_token(token):
        try:
            decoded_token = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired!")
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token!")
