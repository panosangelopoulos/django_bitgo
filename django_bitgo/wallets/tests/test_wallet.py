import pytest

from django_bitgo.client import BitGoClient
from django_bitgo.exceptions import BitGoException
from django_bitgo.wallets.wallet import Wallet

BASE_URL = "https://app.bitgo-test.com/api/v2"


@pytest.fixture
def client():
    return BitGoClient(access_token="my-token")


def test_list_wallets_sends_default_query_params(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet", json={"wallets": []})

    wallet = Wallet(client=client)
    result = wallet.list_wallets()

    assert result == {"wallets": []}
    assert requests_mock.last_request.qs == {"limit": ["25"], "alltokens": ["false"]}


def test_list_wallets_includes_prev_id_when_given(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet", json={"wallets": []})

    wallet = Wallet(client=client)
    wallet.list_wallets(prev_id="abc")

    assert requests_mock.last_request.qs["previd"] == ["abc"]


def test_get_wallet_requires_wallet_id(client):
    wallet = Wallet(client=client)

    with pytest.raises(BitGoException):
        wallet.get_wallet()


def test_get_wallet_uses_constructor_wallet_id(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet/w1", json={"id": "w1"})

    wallet = Wallet(client=client, wallet_id="w1")
    result = wallet.get_wallet()

    assert result == {"id": "w1"}


def test_get_wallet_explicit_id_overrides_constructor(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet/w2", json={"id": "w2"})

    wallet = Wallet(client=client, wallet_id="w1")
    result = wallet.get_wallet(wallet_id="w2")

    assert result == {"id": "w2"}


def test_create_wallet_posts_json_payload(client, requests_mock):
    requests_mock.post(f"{BASE_URL}/tbtc/wallet/add", json={"id": "w1"})

    wallet = Wallet(client=client)
    payload = {"label": "test", "m": 2, "n": 3, "keys": ["k1", "k2", "k3"]}
    result = wallet.create_wallet(payload=payload)

    assert result == {"id": "w1"}
    assert requests_mock.last_request.json() == payload
