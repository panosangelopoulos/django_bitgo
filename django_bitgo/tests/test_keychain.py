import pytest

from django_bitgo.exceptions import BitGoException
from django_bitgo.keychain import Keychain


@pytest.mark.parametrize(
    "call, method, path, body, qs",
    [
        (lambda k: k.list_keys(), "GET", "tbtc/key", None, {}),
        (
            lambda k: k.list_keys(limit=5, prev_id="p1"),
            "GET",
            "tbtc/key",
            None,
            {"limit": ["5"], "prevId": ["p1"]},
        ),
        (lambda k: k.get_key("k1"), "GET", "tbtc/key/k1", None, {}),
        (
            lambda k: k.list_wallet_keys(["w1", "w2"]),
            "GET",
            "keys",
            None,
            {"walletIds": ["w1", "w2"]},
        ),
        (
            lambda k: k.add_key({"pub": "xpub1"}),
            "POST",
            "tbtc/key",
            {"pub": "xpub1"},
            {},
        ),
        (
            lambda k: k.create_bitgo_key(enterprise="e1"),
            "POST",
            "tbtc/key",
            {"source": "bitgo", "enterprise": "e1"},
            {},
        ),
        (
            lambda k: k.create_backup_key(),
            "POST",
            "tbtc/key",
            {"source": "backup"},
            {},
        ),
        (
            lambda k: k.get_tss_pubkey(coin="tsol", enterprise_id="e1"),
            "GET",
            "tsol/tss/pubkey",
            None,
            {"enterpriseId": ["e1"]},
        ),
    ],
)
def test_keychain_endpoints(client, check_call, call, method, path, body, qs):
    check_call(lambda: call(Keychain(client=client)), method, path, body=body, qs=qs)


@pytest.mark.parametrize(
    "call",
    [
        lambda k: k.get_key(""),
        lambda k: k.list_wallet_keys([]),
        lambda k: k.add_key({}),
    ],
)
def test_keychain_validation(client, call):
    with pytest.raises(BitGoException):
        call(Keychain(client=client))
