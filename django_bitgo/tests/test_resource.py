import pytest

from django_bitgo.exceptions import BitGoException
from django_bitgo.resource import Resource, compact, iter_pages, require
from django_bitgo.wallets.wallet import Wallet

BASE_URL = "https://app.bitgo-test.com/api/v2"


def test_require_raises_with_name():
    with pytest.raises(BitGoException) as exc:
        require("", "Wallet id")

    assert str(exc.value) == "Wallet id is missing but required."


def test_compact_drops_none_only():
    assert compact(a=None, b=0, c=False, d="x") == {"b": 0, "c": False, "d": "x"}


def test_resource_falls_back_to_settings_wallet_id(client, bitgo_settings):
    bitgo_settings.BITGO_WALLET_ID = "from-settings"

    assert Resource(client=client).wallet_id == "from-settings"


def test_empty_response_body_returns_empty_dict(client, requests_mock):
    requests_mock.delete(f"{BASE_URL}/tbtc/wallet/w1", status_code=204, text="")

    assert Wallet(client=client).remove_wallet(wallet_id="w1") == {}


def test_iter_pages_follows_next_batch_prev_id(client, requests_mock):
    requests_mock.get(
        f"{BASE_URL}/tbtc/wallet",
        [
            {"json": {"wallets": [1], "nextBatchPrevId": "p2"}},
            {"json": {"wallets": [2]}},
        ],
    )

    pages = list(iter_pages(Wallet(client=client).list_wallets, coin="tbtc"))

    assert [p["wallets"] for p in pages] == [[1], [2]]
    assert requests_mock.request_history[1].qs["previd"] == ["p2"]
