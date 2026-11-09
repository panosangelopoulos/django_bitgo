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


@pytest.mark.parametrize(
    "call, method, path, body, qs",
    [
        (
            lambda w: w.list_all_wallets(params={"coin": "tbtc"}),
            "GET",
            "wallets",
            None,
            {"limit": ["25"], "coin": ["tbtc"]},
        ),
        (lambda w: w.count_wallets(), "GET", "wallets/count", None, {}),
        (
            lambda w: w.get_wallet(params={"allTokens": True}),
            "GET",
            "tbtc/wallet/w1",
            None,
            {"allTokens": ["true"]},
        ),
        (lambda w: w.get_wallet_by_id(), "GET", "wallet/w1", None, {}),
        (
            lambda w: w.get_wallet_by_address("addr1"),
            "GET",
            "tbtc/wallet/address/addr1",
            None,
            {},
        ),
        (
            lambda w: w.update_wallet({"label": "new"}),
            "PUT",
            "tbtc/wallet/w1",
            {"label": "new"},
            {},
        ),
        (lambda w: w.remove_wallet(), "DELETE", "tbtc/wallet/w1", None, {}),
        (lambda w: w.remove_user("u1"), "DELETE", "tbtc/wallet/w1/user/u1", None, {}),
        (
            lambda w: w.freeze_wallet(3600, payload={"reason": "incident"}),
            "POST",
            "tbtc/wallet/w1/freeze",
            {"duration": 3600, "reason": "incident"},
            {},
        ),
        (lambda w: w.get_total_balances(), "GET", "wallet/balances", None, {}),
        (
            lambda w: w.get_total_balances(coin="tbtc"),
            "GET",
            "tbtc/wallet/balances",
            None,
            {},
        ),
        (
            lambda w: w.get_maximum_spendable(params={"feeRate": 1000}),
            "GET",
            "tbtc/wallet/w1/maximumSpendable",
            None,
            {"feeRate": ["1000"]},
        ),
        (
            lambda w: w.list_unspents(prev_id="p1"),
            "GET",
            "tbtc/wallet/w1/unspents",
            None,
            {"limit": ["25"], "prevId": ["p1"]},
        ),
        (
            lambda w: w.build_transaction({"recipients": []}),
            "POST",
            "tbtc/wallet/w1/tx/build",
            {"recipients": []},
            {},
        ),
        (
            lambda w: w.send_transaction({"halfSigned": {"txHex": "ab"}}),
            "POST",
            "tbtc/wallet/w1/tx/send",
            {"halfSigned": {"txHex": "ab"}},
            {},
        ),
        (
            lambda w: w.initiate_transaction({"recipients": []}),
            "POST",
            "tbtc/wallet/w1/tx/initiate",
            {"recipients": []},
            {},
        ),
        (
            lambda w: w.change_fee("tx1", payload={"fee": {"unit": "baseUnit"}}),
            "POST",
            "tbtc/wallet/w1/tx/changeFee",
            {"txid": "tx1", "fee": {"unit": "baseUnit"}},
            {},
        ),
        (
            lambda w: w.build_consolidate_unspents(payload={"limit": 100}),
            "POST",
            "tbtc/wallet/w1/consolidateUnspents",
            {"limit": 100},
            {},
        ),
        (
            lambda w: w.build_consolidate_account(coin="teth"),
            "POST",
            "teth/wallet/w1/consolidateAccount/build",
            None,
            {},
        ),
    ],
)
def test_wallet_endpoints(client, check_call, call, method, path, body, qs):
    wallet = Wallet(client=client, wallet_id="w1")

    check_call(lambda: call(wallet), method, path, body=body, qs=qs)


@pytest.mark.parametrize(
    "call",
    [
        lambda w: w.update_wallet({"label": "x"}),
        lambda w: w.remove_wallet(),
        lambda w: w.freeze_wallet(10),
        lambda w: w.build_transaction({}),
        lambda w: w.get_wallet_by_address(""),
    ],
)
def test_wallet_methods_validate_required_ids(client, call):
    with pytest.raises(BitGoException):
        call(Wallet(client=client))
