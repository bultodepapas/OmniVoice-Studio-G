"""Canonical authentication decision shared by HTTP, WS, and dependencies."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from core.auth import (
    ADMIN_CAPABILITIES,
    LOOPBACK_CAPABILITIES,
    AuthPrincipal,
    CredentialTransport,
    PrincipalKind,
    is_local_host,
    principal_for,
    resolve_principal,
)
from services.admin_sessions import AdminSessionStore


MASTER = "MASTER_DO_NOT_LEAK_7d29"


class Connection:
    def __init__(
        self,
        *,
        host: str = "10.0.0.5",
        headers: dict[str, str] | None = None,
        query: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        scope_type: str = "http",
        path: str = "/v1/audio/voices",
        pin: str | None = None,
    ) -> None:
        network_share = SimpleNamespace(pin=pin) if pin is not None else None
        self.app = SimpleNamespace(state=SimpleNamespace(network_share=network_share))
        self.client = SimpleNamespace(host=host) if host else None
        self.headers = headers or {}
        self.query_params = query or {}
        self.cookies = cookies or {}
        self.scope = {
            "type": scope_type,
            "path": path,
            "state": {},
            "client": (host, 1),
        }


@pytest.fixture
def store() -> AdminSessionStore:
    return AdminSessionStore(pepper=b"x" * 32)


def test_loopback_principal_has_native_capability(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)

    principal = resolve_principal(Connection(host="127.0.0.1"), store=store)

    assert principal.kind is PrincipalKind.LOOPBACK
    assert principal.capabilities == LOOPBACK_CAPABILITIES
    assert principal.transport is CredentialTransport.NONE


def test_principal_capability_helper_is_explicit():
    principal = AuthPrincipal(PrincipalKind.API_KEY, ADMIN_CAPABILITIES)

    assert principal.allows("consume") is True
    assert principal.allows("admin") is True
    assert principal.allows("native") is False


def test_trusted_network_parser_ignores_invalid_entries_and_maps_ipv4(monkeypatch):
    monkeypatch.setenv(
        "OMNIVOICE_TRUSTED_NETWORKS",
        "not-a-network, 10.0.0.0/8",
    )

    assert is_local_host("10.2.3.4") is True
    assert is_local_host("::ffff:10.2.3.4") is True
    assert is_local_host("192.168.1.1") is False
    assert is_local_host("not-an-address") is False
    assert is_local_host(None) is False


def test_valid_master_header_produces_admin_principal(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", f"  {MASTER}  ")

    principal = resolve_principal(
        Connection(headers={"authorization": f"Bearer {MASTER}"}), store=store
    )

    assert principal.kind is PrincipalKind.API_KEY
    assert principal.capabilities == ADMIN_CAPABILITIES
    assert principal.transport is CredentialTransport.HEADER
    assert MASTER not in repr(principal)


def test_valid_session_header_produces_admin_principal(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    session = store.issue(MASTER)

    principal = resolve_principal(
        Connection(headers={"authorization": f"Bearer {session.token}"}), store=store
    )

    assert principal.kind is PrincipalKind.ADMIN_SESSION
    assert principal.capabilities == ADMIN_CAPABILITIES
    assert principal.transport is CredentialTransport.HEADER
    assert principal.credential_id
    assert session.token not in repr(principal)


def test_valid_session_cookie_produces_admin_principal(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    session = store.issue(MASTER)

    principal = resolve_principal(
        Connection(cookies={"ov_session": session.token}), store=store
    )

    assert principal.kind is PrincipalKind.ADMIN_SESSION
    assert principal.transport is CredentialTransport.COOKIE


def test_query_and_legacy_cookie_remain_master_compatibility_channels(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)

    query = resolve_principal(Connection(query={"api_key": MASTER}), store=store)
    cookie = resolve_principal(Connection(cookies={"ov_key": MASTER}), store=store)

    assert query.kind is PrincipalKind.API_KEY
    assert query.transport is CredentialTransport.QUERY
    assert cookie.kind is PrincipalKind.API_KEY
    assert cookie.transport is CredentialTransport.LEGACY_COOKIE


def test_invalid_nonempty_explicit_header_is_authoritative(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    session = store.issue(MASTER)

    principal = resolve_principal(
        Connection(
            headers={"authorization": "Bearer wrong"},
            query={"api_key": MASTER},
            cookies={"ov_session": session.token, "ov_key": MASTER},
        ),
        store=store,
    )

    assert principal.kind is PrincipalKind.ANONYMOUS
    assert principal.transport is CredentialTransport.HEADER


@pytest.mark.parametrize("authorization", ["Basic Zm9vOmJhcg==", "Bearer"])
def test_unsupported_or_malformed_authorization_cannot_fall_back_to_cookie(
    monkeypatch,
    store,
    authorization,
):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    session = store.issue(MASTER)

    principal = resolve_principal(
        Connection(
            headers={"authorization": authorization},
            cookies={"ov_session": session.token, "ov_key": MASTER},
        ),
        store=store,
    )

    assert principal.kind is PrincipalKind.ANONYMOUS
    assert principal.transport is CredentialTransport.HEADER


def test_whitespace_header_and_query_fall_back_to_session_cookie(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    session = store.issue(MASTER)

    principal = resolve_principal(
        Connection(
            headers={"authorization": "Bearer    "},
            query={"api_key": "   "},
            cookies={"ov_session": session.token},
        ),
        store=store,
    )

    assert principal.kind is PrincipalKind.ADMIN_SESSION
    assert principal.transport is CredentialTransport.COOKIE


def test_invalid_session_cookie_is_authoritative_over_legacy_master_cookie(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)

    principal = resolve_principal(
        Connection(
            cookies={
                "ov_session": "ovs_admin_session_" + "a" * 43,
                "ov_key": MASTER,
            }
        ),
        store=store,
    )

    assert principal.kind is PrincipalKind.ANONYMOUS
    assert principal.transport is CredentialTransport.COOKIE


def test_trusted_network_is_consumption_only(monkeypatch, store):
    monkeypatch.delenv("OMNIVOICE_API_KEY", raising=False)
    monkeypatch.setenv("OMNIVOICE_TRUSTED_NETWORKS", "10.0.0.0/24")

    principal = resolve_principal(Connection(host="10.0.0.5"), store=store)

    assert principal.kind is PrincipalKind.TRUSTED_NETWORK
    assert principal.capabilities == frozenset({"consume"})


def test_valid_api_key_beats_trusted_network_identity(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    monkeypatch.setenv("OMNIVOICE_TRUSTED_NETWORKS", "10.0.0.0/24")

    principal = resolve_principal(
        Connection(host="10.0.0.5", headers={"authorization": f"Bearer {MASTER}"}),
        store=store,
    )

    assert principal.kind is PrincipalKind.API_KEY


def test_pin_is_consumption_only(monkeypatch, store):
    monkeypatch.delenv("OMNIVOICE_API_KEY", raising=False)

    principal = resolve_principal(
        Connection(headers={"x-omnivoice-pin": "123456"}, pin="123456"),
        store=store,
    )

    assert principal.kind is PrincipalKind.PIN
    assert principal.capabilities == frozenset({"consume"})


def test_wrong_pin_is_anonymous(monkeypatch, store):
    monkeypatch.delenv("OMNIVOICE_API_KEY", raising=False)

    principal = resolve_principal(
        Connection(headers={"x-omnivoice-pin": "654321"}, pin="123456"),
        store=store,
    )

    assert principal.kind is PrincipalKind.ANONYMOUS


def test_ws_ticket_is_consumed_and_attached_once(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    session = store.issue(MASTER)
    ticket = store.issue_ws_ticket(session.token, "/ws/events", MASTER)
    connection = Connection(
        scope_type="websocket",
        path="/ws/events",
        query={"ws_ticket": ticket.token},
    )

    first = resolve_principal(connection, store=store)
    second = principal_for(connection, store=store)

    assert first.kind is PrincipalKind.ADMIN_SESSION
    assert first.transport is CredentialTransport.WS_TICKET
    assert second is first
    assert store.consume_ws_ticket(ticket.token, "/ws/events", MASTER) is None


def test_invalid_ws_ticket_is_authoritative_over_legacy_query_key(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    connection = Connection(
        scope_type="websocket",
        path="/ws/events",
        query={
            "ws_ticket": "ovs_ws_ticket_" + "a" * 43,
            "api_key": MASTER,
        },
    )

    principal = resolve_principal(connection, store=store)

    assert principal.kind is PrincipalKind.ANONYMOUS
    assert principal.transport is CredentialTransport.WS_TICKET


def test_key_rotation_invalidates_attached_session_only_on_new_scope(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    session = store.issue(MASTER)
    first_connection = Connection(headers={"authorization": f"Bearer {session.token}"})
    assert resolve_principal(first_connection, store=store).kind is PrincipalKind.ADMIN_SESSION

    monkeypatch.setenv("OMNIVOICE_API_KEY", "rotated")
    next_request = resolve_principal(
        Connection(headers={"authorization": f"Bearer {session.token}"}), store=store
    )

    assert next_request.kind is PrincipalKind.ANONYMOUS


def test_key_removal_cannot_revive_session_when_same_key_returns(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    session = store.issue(MASTER)

    monkeypatch.delenv("OMNIVOICE_API_KEY")
    while_removed = resolve_principal(
        Connection(headers={"authorization": f"Bearer {session.token}"}),
        store=store,
    )
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    after_restore = resolve_principal(
        Connection(headers={"authorization": f"Bearer {session.token}"}),
        store=store,
    )

    assert while_removed.kind is PrincipalKind.ANONYMOUS
    assert after_restore.kind is PrincipalKind.ANONYMOUS


def test_principal_for_reuses_scope_decision_without_reparsing(monkeypatch, store):
    monkeypatch.setenv("OMNIVOICE_API_KEY", MASTER)
    connection = Connection(headers={"authorization": f"Bearer {MASTER}"})

    first = principal_for(connection, store=store)
    connection.headers = {"authorization": "Bearer wrong"}
    second = principal_for(connection, store=store)

    assert second is first
    assert second.kind is PrincipalKind.API_KEY


def test_principal_dataclass_cannot_carry_a_raw_secret():
    assert "credential" not in AuthPrincipal.__dataclass_fields__
    assert "token" not in AuthPrincipal.__dataclass_fields__
    assert "secret" not in AuthPrincipal.__dataclass_fields__
