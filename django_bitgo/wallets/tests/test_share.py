import pytest

from django_bitgo.exceptions import BitGoException
from django_bitgo.wallets.share import WalletShare


@pytest.mark.parametrize(
    "call, method, path, body, qs",
    [
        (lambda s: s.list_shares(), "GET", "walletshares", None, {}),
        (
            lambda s: s.count_shares("active"),
            "GET",
            "walletshares/count",
            None,
            {"state": ["active"]},
        ),
        (lambda s: s.get_share("s1"), "GET", "tbtc/walletshare/s1", None, {}),
        (
            lambda s: s.create_share("u1", "view"),
            "POST",
            "tbtc/wallet/w1/share",
            {"user": "u1", "permission": "view"},
            {},
        ),
        (
            lambda s: s.accept_share("s1"),
            "POST",
            "tbtc/walletshare/s1",
            {"state": "accepted"},
            {},
        ),
        (
            lambda s: s.reject_share("s1"),
            "POST",
            "tbtc/walletshare/s1",
            {"state": "rejected"},
            {},
        ),
        (lambda s: s.cancel_share("s1"), "DELETE", "tbtc/walletshare/s1", None, {}),
        (
            lambda s: s.resend_share_email("s1"),
            "POST",
            "tbtc/walletshare/s1/resendemail",
            None,
            {},
        ),
    ],
)
def test_share_endpoints(client, check_call, call, method, path, body, qs):
    share = WalletShare(client=client, wallet_id="w1")

    check_call(lambda: call(share), method, path, body=body, qs=qs)


@pytest.mark.parametrize(
    "call",
    [
        lambda s: s.get_share(""),
        lambda s: s.create_share("", "view"),
        lambda s: s.update_share("s1", ""),
        lambda s: s.cancel_share(""),
    ],
)
def test_share_validation(client, call):
    with pytest.raises(BitGoException):
        call(WalletShare(client=client, wallet_id="w1"))
