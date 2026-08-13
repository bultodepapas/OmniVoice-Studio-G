"""Exact-origin CSRF checks for ambient browser authentication."""

from __future__ import annotations

import os
from urllib.parse import SplitResult, urlsplit


CSRF_HEADER = "x-voicestudio-csrf"
CSRF_VALUE = "1"
SAFE_HTTP_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def _origin_tuple(value: str | None) -> tuple[str, str, int | None] | None:
    if not value or value == "null":
        return None
    try:
        parsed: SplitResult = urlsplit(value)
        port = parsed.port
    except (TypeError, ValueError):
        return None
    if (
        not parsed.scheme
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        return None
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https", "tauri"}:
        return None
    if port is None:
        if scheme == "http":
            port = 80
        elif scheme == "https":
            port = 443
    return scheme, parsed.hostname.lower(), port


def configured_allowed_origins() -> frozenset[tuple[str, str, int | None]]:
    raw_port = os.environ.get("OMNIVOICE_UI_PORT", "3901")
    try:
        ui_port = int(raw_port)
    except (TypeError, ValueError):
        ui_port = 3901
    values = os.environ.get(
        "OMNIVOICE_ALLOWED_ORIGINS",
        f"http://localhost:{ui_port},http://127.0.0.1:{ui_port},"
        "tauri://localhost,http://tauri.localhost",
    ).split(",")
    return frozenset(
        origin
        for value in values
        if (origin := _origin_tuple(value.strip())) is not None
    )


def _destination_origin(connection) -> tuple[str, str, int | None] | None:
    url = getattr(connection, "url", None)
    if url is not None:
        try:
            scheme = {"ws": "http", "wss": "https"}.get(url.scheme, url.scheme)
            return _origin_tuple(f"{scheme}://{url.netloc}")
        except AttributeError:
            pass
    scope = getattr(connection, "scope", None)
    headers = getattr(connection, "headers", None) or {}
    if not isinstance(scope, dict):
        return None
    host = headers.get("host", "") if hasattr(headers, "get") else ""
    scheme = {"ws": "http", "wss": "https"}.get(
        scope.get("scheme", "http"),
        scope.get("scheme", "http"),
    )
    return _origin_tuple(f"{scheme}://{host}")


def origin_allowed(connection) -> bool:
    headers = getattr(connection, "headers", None) or {}
    origin_value = headers.get("origin", "") if hasattr(headers, "get") else ""
    presented = _origin_tuple(origin_value)
    if presented is None:
        return False
    return presented == _destination_origin(connection) or presented in configured_allowed_origins()


def cookie_csrf_allowed(connection, *, side_effectful_get: bool = False) -> bool:
    headers = getattr(connection, "headers", None) or {}
    marker = headers.get(CSRF_HEADER, "") if hasattr(headers, "get") else ""
    if marker != CSRF_VALUE or not origin_allowed(connection):
        return False
    method = getattr(connection, "method", None)
    if method is None:
        scope = getattr(connection, "scope", None)
        method = scope.get("method", "GET") if isinstance(scope, dict) else "GET"
    method = str(method).upper()
    if side_effectful_get or method in SAFE_HTTP_METHODS:
        fetch_site = headers.get("sec-fetch-site", "") if hasattr(headers, "get") else ""
        return fetch_site == "same-origin"
    return True
