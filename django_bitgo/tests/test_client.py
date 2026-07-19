import pytest
import requests

from django_bitgo.client import BitGoClient
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
