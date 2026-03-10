from fastapi import Header, HTTPException
import httpx
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings

JWKS_URL = (
    f"{settings.keycloak_url}/realms/{settings.keycloak_realm}/protocol/"
    "openid-connect/certs"
)
ISSUER = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"


def extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")
    return authorization[len("Bearer "):]


async def get_jwks() -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0, trust_env=False) as client:
            r = await client.get(JWKS_URL)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=401, detail=f"Cannot fetch JWKS: {exc}") from exc


async def decode_access_token(token: str) -> dict:
    jwks = await get_jwks()
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=ISSUER,
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc

    if payload.get("azp") != settings.keycloak_client_id:
        raise HTTPException(status_code=401, detail="Invalid azp")

    return payload


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> dict:
    token = extract_bearer_token(authorization)
    payload = await decode_access_token(token)
    return {
        "sub": payload.get("sub"),
        "username": payload.get("preferred_username"),
        "roles": payload.get("realm_access", {}).get("roles", []),
    }

