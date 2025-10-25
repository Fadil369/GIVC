import json
from types import SimpleNamespace
from typing import Dict, List, Optional, Tuple, Union

import pytest  # type: ignore[import-not-found]

import auth.auth_manager as auth_module


REQUEST_EXCEPTIONS = auth_module.requests.exceptions


class DummyResponse:
    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict] = None,
        text: Optional[str] = None,
    ):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text or json.dumps(self._json_data)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise REQUEST_EXCEPTIONS.HTTPError(response=self)

    def json(self) -> Dict:
        return self._json_data


class SessionStub:
    def __init__(self):
        self.headers: Dict[str, str] = {}
        self.cert = None
        self.verify = True
        self.mounted: List[Tuple[str, object]] = []
        self.request_calls: List[Dict] = []
        self.get_calls: List[Tuple[str, Dict]] = []
        self.next_request_response: Optional[DummyResponse] = DummyResponse()
        self.next_request_exception: Optional[Exception] = None
        self.next_get_response: Union[
            DummyResponse, Exception
        ] = DummyResponse()
        self.closed = False

    def mount(self, prefix: str, adapter: object) -> None:
        self.mounted.append((prefix, adapter))

    def request(
        self,
        method: str,
        url: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None,
    ):
        self.request_calls.append(
            {
                "method": method,
                "url": url,
                "json": json,
                "params": params,
                "headers": headers,
                "timeout": timeout,
            }
        )

        if self.next_request_exception:
            exc = self.next_request_exception
            self.next_request_exception = None
            raise exc

        assert self.next_request_response is not None
        return self.next_request_response

    def get(self, url: str, **kwargs):
        self.get_calls.append((url, kwargs))

        if isinstance(self.next_get_response, Exception):
            raise self.next_get_response

        return self.next_get_response

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def manager_with_stub(monkeypatch):
    stub = SessionStub()

    monkeypatch.setattr(auth_module.requests, "Session", lambda: stub)

    manager = auth_module.AuthenticationManager()
    return SimpleNamespace(manager=manager, session=stub)


def test_session_setup_adds_retries_and_headers(manager_with_stub):
    session = manager_with_stub.session

    assert session.mounted
    assert "Content-Type" in session.headers
    assert session.headers["User-Agent"] == "NPHIES-Python-Client/1.0"


def test_get_auth_headers_returns_expected_values(manager_with_stub):
    headers = manager_with_stub.manager.get_auth_headers()

    assert headers["X-License-Number"] == auth_module.settings.NPHIES_LICENSE
    organization_id = auth_module.settings.NPHIES_ORGANIZATION_ID
    assert headers["X-Organization-ID"] == organization_id
    assert headers["X-Provider-ID"] == auth_module.settings.NPHIES_PROVIDER_ID


def test_make_request_success_returns_response(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_request_response = DummyResponse(json_data={"result": "ok"})

    response = manager.make_request("GET", "https://nphies.sa/status")

    assert response.json()["result"] == "ok"
    # Verify auth headers were included
    stub_headers = stub.request_calls[0]["headers"]
    assert "X-License-Number" in stub_headers


def test_make_request_propagates_timeout(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_request_exception = REQUEST_EXCEPTIONS.Timeout()

    with pytest.raises(REQUEST_EXCEPTIONS.Timeout):
        manager.make_request("GET", "https://nphies.sa/status")


def test_make_request_raises_for_http_error(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_request_response = DummyResponse(
        status_code=500,
        text="server error",
    )

    with pytest.raises(REQUEST_EXCEPTIONS.HTTPError):
        manager.make_request("POST", "https://nphies.sa/status")


def test_test_connection_reports_success(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_get_response = DummyResponse(status_code=200)

    success, message = manager.test_connection()

    assert success is True
    assert "Connection successful" in message


def test_test_connection_handles_errors(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_get_response = REQUEST_EXCEPTIONS.ConnectionError()

    success, message = manager.test_connection()

    assert success is False
    assert "Connection failed" in message


def test_close_closes_underlying_session(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session

    manager.close()

    assert stub.closed is True


def test_post_method_calls_make_request(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_request_response = DummyResponse(json_data={"posted": True})

    response = manager.post("https://nphies.sa/api", {"data": "value"})

    assert response.json()["posted"] is True
    assert stub.request_calls[0]["method"] == "POST"


def test_get_method_calls_make_request(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_request_response = DummyResponse(json_data={"got": True})

    response = manager.get("https://nphies.sa/api")

    assert response.json()["got"] is True
    assert stub.request_calls[0]["method"] == "GET"


def test_make_request_merges_additional_headers(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_request_response = DummyResponse()

    manager.make_request(
        "POST",
        "https://nphies.sa/api",
        additional_headers={"X-Custom": "value"}
    )

    headers = stub.request_calls[0]["headers"]
    assert headers["X-Custom"] == "value"
    assert "X-License-Number" in headers


def test_make_request_handles_connection_error(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_request_exception = REQUEST_EXCEPTIONS.ConnectionError()

    with pytest.raises(REQUEST_EXCEPTIONS.ConnectionError):
        manager.make_request("GET", "https://nphies.sa/api")


def test_make_request_includes_params(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_request_response = DummyResponse()

    manager.make_request(
        "GET",
        "https://nphies.sa/api",
        params={"filter": "active"}
    )

    assert stub.request_calls[0]["params"] == {"filter": "active"}


def test_test_connection_handles_server_error(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_get_response = DummyResponse(status_code=503)

    success, message = manager.test_connection()

    assert success is False
    assert "Server error" in message


def test_test_connection_handles_timeout(manager_with_stub):
    manager = manager_with_stub.manager
    stub = manager_with_stub.session
    stub.next_get_response = REQUEST_EXCEPTIONS.Timeout()

    success, message = manager.test_connection()

    assert success is False
    assert "timeout" in message.lower()


def test_init_with_certificates_enabled(tmp_path, monkeypatch):
    """Test initialization with certificates enabled"""
    # Create dummy cert files
    cert_file = tmp_path / "client.crt"
    key_file = tmp_path / "client.key"
    ca_file = tmp_path / "ca.crt"
    
    cert_file.write_text("dummy cert")
    key_file.write_text("dummy key")
    ca_file.write_text("dummy ca")
    
    # Mock settings
    settings_mock = SimpleNamespace(
        ENVIRONMENT="production",
        NPHIES_BASE_URL="https://nphies.sa",
        API_KEY="test-key",
        REQUEST_TIMEOUT=30,
        MAX_RETRIES=3,
        RETRY_DELAY=1,
        BACKOFF_FACTOR=1,
        use_certificates=True,
        CERT_FILE_PATH=str(cert_file),
        CERT_KEY_PATH=str(key_file),
        CA_BUNDLE_PATH=str(ca_file)
    )
    
    monkeypatch.setattr("auth.auth_manager.settings", settings_mock)
    
    # Create manager instance
    from auth.auth_manager import AuthenticationManager
    manager = AuthenticationManager()
    
    # Verify certificates were configured
    assert manager.session.cert == (str(cert_file), str(key_file))
    assert manager.session.verify == str(ca_file)


def test_configure_certificates_missing_cert_file(tmp_path, monkeypatch):
    """Test certificate configuration with missing cert file"""
    key_file = tmp_path / "client.key"
    key_file.write_text("dummy key")
    
    settings_mock = SimpleNamespace(
        ENVIRONMENT="production",
        NPHIES_BASE_URL="https://nphies.sa",
        API_KEY="test-key",
        REQUEST_TIMEOUT=30,
        MAX_RETRIES=3,
        RETRY_DELAY=1,
        BACKOFF_FACTOR=1,
        use_certificates=True,
        CERT_FILE_PATH="/nonexistent/cert.crt",
        CERT_KEY_PATH=str(key_file),
        CA_BUNDLE_PATH=None
    )
    
    monkeypatch.setattr("auth.auth_manager.settings", settings_mock)
    
    from auth.auth_manager import AuthenticationManager
    manager = AuthenticationManager()
    
    # Should not have configured certs (gracefully handled missing file)
    assert manager.session.cert is None


def test_configure_certificates_exception_handling(tmp_path, monkeypatch):
    """Test certificate configuration exception handling"""
    settings_mock = SimpleNamespace(
        ENVIRONMENT="production",
        NPHIES_BASE_URL="https://nphies.sa",
        API_KEY="test-key",
        REQUEST_TIMEOUT=30,
        MAX_RETRIES=3,
        RETRY_DELAY=1,
        BACKOFF_FACTOR=1,
        use_certificates=True,
        CERT_FILE_PATH=None,  # Invalid - will cause exception
        CERT_KEY_PATH=None,
        CA_BUNDLE_PATH=None
    )
    
    monkeypatch.setattr("auth.auth_manager.settings", settings_mock)
    
    # Should raise exception due to invalid path
    from auth.auth_manager import AuthenticationManager
    import pytest
    with pytest.raises(Exception):
        manager = AuthenticationManager()
