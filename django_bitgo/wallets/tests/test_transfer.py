import pytest

from django_bitgo.client import BitGoClient
from django_bitgo.exceptions import BitGoException
from django_bitgo.wallets.transfer import Transfer

BASE_URL = "https://app.bitgo-test.com/api/v2"


@pytest.fixture
def client():
    return BitGoClient(access_token="my-token")


def test_list_transfers_requires_wallet_id(client):
    transfer = Transfer(client=client)

    with pytest.raises(BitGoException):
        transfer.list_transfers()


def test_list_transfers_uses_constructor_wallet_id(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet/w1/transfer", json={"transfers": []})

    transfer = Transfer(client=client, wallet_id="w1")
    result = transfer.list_transfers()

    assert result == {"transfers": []}
    assert requests_mock.last_request.qs == {"limit": ["25"], "alltokens": ["false"]}


def test_list_transfers_includes_prev_id_when_given(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet/w1/transfer", json={"transfers": []})

    transfer = Transfer(client=client, wallet_id="w1")
    transfer.list_transfers(prev_id="abc")

    assert requests_mock.last_request.qs["previd"] == ["abc"]


def test_get_transfer_requires_wallet_id(client):
    transfer = Transfer(client=client)

    with pytest.raises(BitGoException):
        transfer.get_transfer(transfer_id="t1")


def test_get_transfer_requires_transfer_id(client):
    transfer = Transfer(client=client, wallet_id="w1")

    with pytest.raises(BitGoException):
        transfer.get_transfer(transfer_id="")


def test_get_transfer_returns_json(client, requests_mock):
    requests_mock.get(f"{BASE_URL}/tbtc/wallet/w1/transfer/t1", json={"id": "t1"})

    transfer = Transfer(client=client, wallet_id="w1")
    result = transfer.get_transfer(transfer_id="t1")

    assert result == {"id": "t1"}


@pytest.mark.parametrize(
    "call, method, path, body, qs",
    [
        (
            lambda t: t.list_transfers(params={"state": "confirmed"}),
            "GET",
            "tbtc/wallet/w1/transfer",
            None,
            {"limit": ["25"], "allTokens": ["false"], "state": ["confirmed"]},
        ),
        (
            lambda t: t.get_transfer_by_sequence_id("seq1"),
            "GET",
            "tbtc/wallet/w1/transfer/sequenceId/seq1",
            None,
            {},
        ),
        (
            lambda t: t.comment_transfer("t1", "hello"),
            "POST",
            "tbtc/wallet/w1/transfer/t1/comment",
            {"comment": "hello"},
            {},
        ),
        (
            lambda t: t.list_enterprise_transfers("e1", prev_id="p1"),
            "GET",
            "enterprise/e1/transfer",
            None,
            {"limit": ["25"], "prevId": ["p1"]},
        ),
        (
            lambda t: t.get_fee_estimate(num_blocks=2),
            "GET",
            "tbtc/tx/fee",
            None,
            {"numBlocks": ["2"]},
        ),
        (lambda t: t.get_fee_estimate(), "GET", "tbtc/tx/fee", None, {}),
        (lambda t: t.get_transaction("tx1"), "GET", "tbtc/tx/tx1", None, {}),
    ],
)
def test_transfer_endpoints(client, check_call, call, method, path, body, qs):
    transfer = Transfer(client=client, wallet_id="w1")

    check_call(lambda: call(transfer), method, path, body=body, qs=qs)


@pytest.mark.parametrize(
    "call",
    [
        lambda t: t.get_transfer_by_sequence_id(""),
        lambda t: t.comment_transfer("", "x"),
        lambda t: t.list_enterprise_transfers(""),
        lambda t: t.get_transaction(""),
    ],
)
def test_transfer_methods_validate_required_ids(client, call):
    with pytest.raises(BitGoException):
        call(Transfer(client=client, wallet_id="w1"))
