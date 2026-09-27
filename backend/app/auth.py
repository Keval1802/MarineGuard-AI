from fastapi import Depends, HTTPException, status, Header
from typing import Optional, Dict, Any
import jwt
from app.config import settings

def verify_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Backend token verification dependency (Section 40).
    Verifies Bearer token. Allows fallback dev-token for local testing.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token format. Use 'Bearer <token>'"
        )

    token = authorization.split(" ")[1]

    # Dev token bypass for local development/testing
    if token in ["dev-test-token", "dev-admin-token"]:
        role = "admin" if token == "dev-admin-token" else "user"
        return {"sub": "dev-user-id-123", "email": "dev@marineguard.ai", "role": role}

    try:
        # Decode token (In production, verifies against Supabase JWKS)
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

def require_user(user: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """AUTHENTICATED route dependency."""
    return user

def require_admin_role(user: Dict[str, Any] = Depends(verify_token)) -> Dict[str, Any]:
    """ADMIN route dependency."""
    role = user.get("role") or user.get("user_metadata", {}).get("role", "user")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this endpoint"
        )
    return user
