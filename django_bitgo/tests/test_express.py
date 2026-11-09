import pytest

from django_bitgo.client import ExpressClient
from django_bitgo.exceptions import BitGoException
from django_bitgo.express import Express

EXPRESS_BASE = "http://localhost:3080/api/v2/"


@pytest.fixture
def express_client():
    return ExpressClient(access_token="my-token")


def test_express_defaults_to_express_client(monkeypatch):
    monkeypatch.setenv("BITGO_ACCESS_TOKEN", "env-token")

    assert isinstance(Express().client, ExpressClient)


@pytest.mark.parametrize(
    "call, method, path, body, qs",
    [
        (lambda x: x.ping(), "GET", "pingexpress", None, {}),
        (
            lambda x: x.generate_wallet(
                "main", "e1", passphrase="pw", include_keychains=True
            ),
            "POST",
            "tbtc/wallet/generate",
            {"label": "main", "enterprise": "e1", "passphrase": "pw"},
            {"includeKeychains": ["true"]},
        ),
        (
            lambda x: x.share_wallet("a@b.c", "view,spend", wallet_passphrase="pw"),
            "POST",
            "tbtc/wallet/w1/share",
            {"email": "a@b.c", "permissions": "view,spend", "walletPassphrase": "pw"},
            {},
        ),
        (
            lambda x: x.accept_share("s1", new_wallet_passphrase="pw"),
            "POST",
            "tbtc/walletshare/s1/acceptshare",
            {"newWalletPassphrase": "pw"},
            {},
        ),
        (
            lambda x: x.send_coins("addr", "1000", "pw", payload={"feeRate": 2000}),
            "POST",
            "tbtc/wallet/w1/sendcoins",
            {
                "address": "addr",
                "amount": "1000",
                "walletPassphrase": "pw",
                "feeRate": 2000,
            },
            {},
        ),
        (
            lambda x: x.send_many([{"address": "a", "amount": "1"}], "pw"),
            "POST",
            "tbtc/wallet/w1/sendmany",
            {"recipients": [{"address": "a", "amount": "1"}], "walletPassphrase": "pw"},
            {},
        ),
        (
            lambda x: x.sign_transaction({"txPrebuild": {}, "walletPassphrase": "pw"}),
            "POST",
            "tbtc/wallet/w1/signtx",
            {"txPrebuild": {}, "walletPassphrase": "pw"},
            {},
        ),
        (
            lambda x: x.sign_tss_transaction({"txRequestId": "tr1"}, coin="tsol"),
            "POST",
            "tsol/wallet/w1/signtxtss",
            {"txRequestId": "tr1"},
            {},
        ),
        (
            lambda x: x.accelerate_transaction("pw", cpfp_tx_ids=["tx1"]),
            "POST",
            "tbtc/wallet/w1/acceleratetx",
            {"cpfpTxIds": ["tx1"], "walletPassphrase": "pw"},
            {},
        ),
        (
            lambda x: x.consolidate_unspents("pw", payload={"numUnspentsToMake": 1}),
            "POST",
            "tbtc/wallet/w1/consolidateunspents",
            {"walletPassphrase": "pw", "numUnspentsToMake": 1},
            {},
        ),
        (
            lambda x: x.fanout_unspents("pw"),
            "POST",
            "tbtc/wallet/w1/fanoutunspents",
            {"walletPassphrase": "pw"},
            {},
        ),
        (
            lambda x: x.consolidate_account("pw"),
            "POST",
            "teth/wallet/w1/consolidateAccount",
            {"walletPassphrase": "pw"},
            {},
        ),
        (
            lambda x: x.sweep("addr", "pw"),
            "POST",
            "tbtc/wallet/w1/sweep",
            {"address": "addr", "walletPassphrase": "pw"},
            {},
        ),
        (
            lambda x: x.verify_address("addr"),
            "POST",
            "tbtc/verifyaddress",
            {"address": "addr"},
            {},
        ),
        (
            lambda x: x.canonical_address("addr", version="base58"),
            "POST",
            "tbch/canonicaladdress",
            {"address": "addr", "version": "base58"},
            {},
        ),
        (
            lambda x: x.is_wallet_address("0xabc", [{"pub": "p"}]),
            "POST",
            "teth/wallet/w1/iswalletaddress",
            {"address": "0xabc", "keychains": [{"pub": "p"}]},
            {},
        ),
    ],
)
def test_express_endpoints(express_client, check_call, call, method, path, body, qs):
    express = Express(client=express_client, wallet_id="w1")

    check_call(lambda: call(express), method, path, body=body, qs=qs, base=EXPRESS_BASE)


@pytest.mark.parametrize(
    "call",
    [
        lambda x: x.send_coins("", "1", "pw"),
        lambda x: x.send_coins("addr", "1", ""),
        lambda x: x.send_many([], "pw"),
        lambda x: x.accelerate_transaction("pw"),
        lambda x: x.generate_wallet("main", ""),
        lambda x: x.sweep("", "pw"),
        lambda x: x.consolidate_unspents(""),
    ],
)
def test_express_validation(express_client, call):
    with pytest.raises(BitGoException):
        call(Express(client=express_client, wallet_id="w1"))


def test_express_send_coins_requires_wallet_id(express_client):
    with pytest.raises(BitGoException):
        Express(client=express_client).send_coins("addr", "1", "pw")
