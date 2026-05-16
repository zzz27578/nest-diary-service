from __future__ import annotations

from fastapi import Header, HTTPException


def verify_bearer_token(expected_token: str, authorization: str | None = Header(default=None)) -> None:
    if not expected_token:
        raise HTTPException(status_code=503, detail="Bot API token is not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bot token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != expected_token:
        raise HTTPException(status_code=403, detail="Invalid bot token")


def verify_bearer_token_from_store(token_getter, authorization: str | None = Header(default=None)) -> None:
    verify_bearer_token(token_getter(), authorization)
