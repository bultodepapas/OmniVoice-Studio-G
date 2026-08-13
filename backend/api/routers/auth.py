"""Short-lived credentials for the first-party remote administration UI."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core.auth import (
    CredentialTransport,
    PrincipalKind,
    authorization_credential_present,
    legacy_master_cookie_valid,
    master_header_valid,
    principal_for,
    remote_api_key,
)
from core.csrf import cookie_csrf_allowed
from services.admin_sessions import (
    SESSION_TTL_SECONDS,
    WS_TICKET_TTL_SECONDS,
    admin_session_store,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


class SessionRequest(BaseModel):
    transport: Literal["cookie", "bearer"]


class WebSocketTicketRequest(BaseModel):
    path: str


def _secure_cookie(request: Request) -> bool:
    # Do not trust arbitrary X-Forwarded-Proto. Proxy trust must be configured
    # at the ASGI server boundary; at this layer the resolved scope is authority.
    return request.url.scheme == "https"


def _set_session_cookie(response: Response, request: Request, token: str, expires_at: float) -> None:
    response.set_cookie(
        "ov_session",
        token,
        max_age=SESSION_TTL_SECONDS,
        expires=datetime.fromtimestamp(expires_at, tz=timezone.utc),
        path="/",
        secure=_secure_cookie(request),
        httponly=True,
        samesite="strict",
    )


def _expire_cookie(response: Response, request: Request, name: str) -> None:
    response.delete_cookie(
        name,
        path="/",
        secure=_secure_cookie(request),
        httponly=name == "ov_session",
        samesite="strict",
    )


@router.post("/session")
def create_session(payload: SessionRequest, request: Request) -> Response:
    configured = remote_api_key()
    if not configured:
        raise HTTPException(status_code=401, detail="API key required")

    authorization_present = authorization_credential_present(request)
    header_authorized = master_header_valid(request)
    legacy_authorized = legacy_master_cookie_valid(request)
    migrating_legacy = False

    if authorization_present:
        if not header_authorized:
            raise HTTPException(status_code=401, detail="API key required")
    elif legacy_authorized:
        if payload.transport != "cookie" or not cookie_csrf_allowed(request):
            raise HTTPException(status_code=403, detail="browser origin rejected")
        migrating_legacy = True
    else:
        raise HTTPException(status_code=401, detail="API key required")

    issued = admin_session_store.issue(configured)
    if payload.transport == "bearer":
        return JSONResponse(
            {
                "token": issued.token,
                "expires_at": issued.expires_at,
                "expires_in": SESSION_TTL_SECONDS,
            },
            status_code=201,
        )

    response = Response(status_code=204)
    _set_session_cookie(response, request, issued.token, issued.expires_at)
    if migrating_legacy or request.cookies.get("ov_key"):
        _expire_cookie(response, request, "ov_key")
    return response


@router.delete("/session", status_code=204)
def delete_session(request: Request) -> Response:
    principal = principal_for(request)
    if principal.kind is PrincipalKind.ADMIN_SESSION:
        if (
            principal.transport is CredentialTransport.COOKIE
            and not cookie_csrf_allowed(request)
        ):
            raise HTTPException(status_code=403, detail="browser origin rejected")
        admin_session_store.revoke_by_credential(principal.credential_id)
    response = Response(status_code=204)
    _expire_cookie(response, request, "ov_session")
    return response


@router.post("/ws-ticket")
def create_ws_ticket(payload: WebSocketTicketRequest, request: Request) -> JSONResponse:
    principal = principal_for(request)
    if principal.kind is not PrincipalKind.ADMIN_SESSION:
        raise HTTPException(status_code=403, detail="admin session required")
    if (
        principal.transport is CredentialTransport.COOKIE
        and not cookie_csrf_allowed(request)
    ):
        raise HTTPException(status_code=403, detail="browser origin rejected")
    try:
        ticket = admin_session_store.issue_ws_ticket_for_credential(
            principal.credential_id,
            payload.path,
            remote_api_key(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    except PermissionError:
        raise HTTPException(status_code=401, detail="admin session required") from None
    return JSONResponse(
        {
            "ticket": ticket.token,
            "expires_at": ticket.expires_at,
            "expires_in": WS_TICKET_TTL_SECONDS,
        },
        status_code=201,
    )
