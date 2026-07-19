import pytest

from django_bitgo.client import BitGoClient
from django_bitgo.exceptions import BitGoException
from django_bitgo.wallets.address import Address

BASE_URL = "https://app.bitgo-test.com/api/v2"


@pytest.fixture
def client():
    return BitGoClient(access_token="my-token")


def test_address_defaults_to_own_client(monkeypatch):
    monkeypatch.setenv("BITGO_ACCESS_TOKEN", "env-token")

    address = Address()

    assert address.client.access_token == "env-token"


def test_address_uses_constructor_wallet_id_as_fallback(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet/w1/addresses", json={"addresses": []})

    address = Address(client=client, wallet_id="w1")
    result = address.list_addresses()

    assert result == {"addresses": []}
    assert requests_mock.last_request.path == "/api/v2/tbtc/wallet/w1/addresses"


def test_list_addresses_explicit_wallet_id_overrides_constructor(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet/w2/addresses", json={"addresses": []})

    address = Address(client=client, wallet_id="w1")
    address.list_addresses(wallet_id="w2")

    assert requests_mock.last_request.path == "/api/v2/tbtc/wallet/w2/addresses"


def test_create_address_posts_payload(client, requests_mock):
    requests_mock.post(f"{BASE_URL}/tbtc/wallet/w1/address", json={"address": "abc"})

    address = Address(client=client, wallet_id="w1")
    result = address.create_address(payload={"label": "test"})

    assert result == {"address": "abc"}
    assert requests_mock.last_request.json() == {"label": "test"}
    assert requests_mock.last_request.headers["Content-Type"] == "application/json"


def test_get_address_requires_address_id(client):
    address = Address(client=client, wallet_id="w1")

    with pytest.raises(BitGoException):
        address.get_address(address_id="")


def test_get_address_returns_json(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet/w1/address/addr1", json={"id": "addr1"})

    address = Address(client=client, wallet_id="w1")
    result = address.get_address(address_id="addr1")

    assert result == {"id": "addr1"}


def test_deploy_address_requires_address_id(client):
    address = Address(client=client, wallet_id="w1")

    with pytest.raises(BitGoException):
        address.deploy_address(address_id="")


def test_deploy_address_posts_to_deployment_endpoint(client, requests_mock):
    requests_mock.post(
        f"{BASE_URL}/tbtc/wallet/w1/address/addr1/deployment", json={"deployed": True}
    )

    address = Address(client=client, wallet_id="w1")
    result = address.deploy_address(address_id="addr1")

    assert result == {"deployed": True}
