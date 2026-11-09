import pytest
import requests

from django_bitgo.client import BitGoClient, ExpressClient
from django_bitgo.exceptions import BitGoException


def test_client_requires_access_token(monkeypatch):
    monkeypatch.delenv("BITGO_ACCESS_TOKEN", raising=False)

    with pytest.raises(BitGoException) as exc:
        BitGoClient()

    assert str(exc.value) == "Access token is required to create a BitGoClient"


def test_client_falls_back_to_env_var(monkeypatch):
    monkeypatch.setenv("BITGO_ACCESS_TOKEN", "env-token")

    client = BitGoClient()

    assert client.access_token == "env-token"


def test_request_sends_bearer_token(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.get(
        "https://app.bitgo-test.com/api/v2/tbtc/wallet/w1/addresses",
        json={"addresses": []},
    )

    client.request(method="GET", path="tbtc/wallet/w1/addresses")

    assert requests_mock.last_request.headers["Authorization"] == "Bearer my-token"


def test_request_does_not_mutate_caller_supplied_headers(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.get(
        "https://app.bitgo-test.com/api/v2/tbtc/wallet/w1/addresses", json={}
    )
    caller_headers = {"X-Custom": "value"}

    client.request(
        method="GET", path="tbtc/wallet/w1/addresses", headers=caller_headers
    )

    assert caller_headers == {"X-Custom": "value"}
    assert requests_mock.last_request.headers["X-Custom"] == "value"
    assert requests_mock.last_request.headers["Authorization"] == "Bearer my-token"


def test_request_raises_bitgo_exception_on_http_error(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.get(
        "https://app.bitgo-test.com/api/v2/tbtc/wallet/w1/addresses",
        status_code=500,
        json={"error": "boom"},
    )

    with pytest.raises(BitGoException):
        client.request(method="GET", path="tbtc/wallet/w1/addresses")


def test_request_sends_json_body(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.post(
        "https://app.bitgo-test.com/api/v2/tbtc/wallet/w1/address", json={}
    )

    client.request(
        method="POST",
        path="tbtc/wallet/w1/address",
        payload={"label": "test"},
    )

    assert requests_mock.last_request.json() == {"label": "test"}
    assert requests_mock.last_request.headers["Content-Type"] == "application/json"


def test_request_sends_query_params(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.get("https://app.bitgo-test.com/api/v2/tbtc/wallet", json={})

    client.request(method="GET", path="tbtc/wallet", params={"limit": 10})

    assert requests_mock.last_request.qs == {"limit": ["10"]}


def test_request_raises_bitgo_exception_on_connection_error(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.get(
        "https://app.bitgo-test.com/api/v2/tbtc/wallet/w1/addresses",
        exc=requests.exceptions.ConnectionError,
    )

    with pytest.raises(BitGoException):
        client.request(method="GET", path="tbtc/wallet/w1/addresses")


def test_request_sends_booleans_as_lowercase_strings(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.get("https://app.bitgo-test.com/api/v2/tbtc/wallet", json={})

    client.request(
        method="GET", path="tbtc/wallet", params={"allTokens": False, "x": True}
    )

    assert "allTokens=false" in requests_mock.last_request.url
    assert "x=true" in requests_mock.last_request.url


def test_request_drops_none_query_params(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.get("https://app.bitgo-test.com/api/v2/tbtc/wallet", json={})

    client.request(method="GET", path="tbtc/wallet", params={"a": None, "b": 1})

    assert requests_mock.last_request.qs == {"b": ["1"]}


def test_http_error_exposes_bitgo_error_details(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.get(
        "https://app.bitgo-test.com/api/v2/tbtc/wallet/w1",
        status_code=404,
        json={"error": "wallet not found", "name": "WalletNotFound", "requestId": "r1"},
    )

    with pytest.raises(BitGoException) as exc:
        client.request(method="GET", path="tbtc/wallet/w1")

    assert exc.value.status_code == 404
    assert exc.value.error_name == "WalletNotFound"
    assert exc.value.request_id == "r1"
    assert exc.value.response_body["error"] == "wallet not found"
    assert "wallet not found" in str(exc.value)


def test_http_error_with_non_json_body(requests_mock):
    client = BitGoClient(access_token="my-token")
    requests_mock.get(
        "https://app.bitgo-test.com/api/v2/tbtc/wallet", status_code=502, text="bad"
    )

    with pytest.raises(BitGoException) as exc:
        client.request(method="GET", path="tbtc/wallet")

    assert exc.value.status_code == 502
    assert exc.value.response_body is None


def test_api_url_override(requests_mock):
    client = BitGoClient(access_token="my-token", api_url="https://other.example/")
    requests_mock.get("https://other.example/api/v2/tbtc/wallet", json={})

    client.request(method="GET", path="tbtc/wallet")

    assert requests_mock.called


def test_express_client_defaults_to_express_url(requests_mock):
    client = ExpressClient(access_token="my-token")
    requests_mock.get("http://localhost:3080/api/v2/pingexpress", json={})

    client.request(method="GET", path="pingexpress")

    assert client.get_api_url() == "http://localhost:3080/"
    assert requests_mock.called


def test_client_defaults_when_settings_are_not_defined(monkeypatch, requests_mock):
    from django.conf import settings

    monkeypatch.delattr(settings, "BITGO_API_URL")
    monkeypatch.delattr(settings, "BITGO_API_VERSION")
    client = BitGoClient(access_token="my-token")
    requests_mock.get("https://app.bitgo-test.com/api/v2/tbtc/wallet", json={})

    client.request(method="GET", path="tbtc/wallet")

    assert requests_mock.called
