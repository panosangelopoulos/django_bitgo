import pytest

from django_bitgo.exceptions import BitGoException
from django_bitgo.wallets.tx_request import TxRequest

INTENT = {"intentType": "payment", "recipients": []}


@pytest.mark.parametrize(
    "call, method, path, body, qs",
    [
        (
            lambda t: t.list_tx_requests(params={"states": "pendingApproval"}),
            "GET",
            "wallet/w1/txrequests",
            None,
            {"states": ["pendingApproval"]},
        ),
        (
            lambda t: t.create_tx_request(INTENT),
            "POST",
            "wallet/w1/txrequests",
            {"intent": INTENT, "apiVersion": "full"},
            {},
        ),
        (
            lambda t: t.cancel_tx_request("tr1", reason="oops"),
            "PUT",
            "wallet/w1/txrequests/tr1",
            {"state": "canceled", "cancellationReason": "oops"},
            {},
        ),
        (
            lambda t: t.list_awaiting_signature(),
            "GET",
            "wallet/w1/txrequests/awaitingsignature",
            None,
            {},
        ),
        (
            lambda t: t.list_enterprise_tx_requests("e1"),
            "GET",
            "enterprise/e1/txrequests",
            None,
            {},
        ),
    ],
)
def test_tx_request_endpoints(client, check_call, call, method, path, body, qs):
    tx_request = TxRequest(client=client, wallet_id="w1")

    check_call(lambda: call(tx_request), method, path, body=body, qs=qs)


def test_get_tx_request_returns_latest(client, requests_mock):
    requests_mock.get(
        "https://app.bitgo-test.com/api/v2/wallet/w1/txrequests",
        json={"txRequests": [{"txRequestId": "tr1"}]},
    )

    result = TxRequest(client=client, wallet_id="w1").get_tx_request("tr1")

    assert result == {"txRequestId": "tr1"}
    assert "txRequestIds=tr1" in requests_mock.last_request.url
    assert "latest=true" in requests_mock.last_request.url


def test_get_tx_request_not_found(client, requests_mock):
    requests_mock.get(
        "https://app.bitgo-test.com/api/v2/wallet/w1/txrequests",
        json={"txRequests": []},
    )

    assert TxRequest(client=client, wallet_id="w1").get_tx_request("tr1") is None


@pytest.mark.parametrize(
    "call",
    [
        lambda t: t.create_tx_request({}),
        lambda t: t.update_tx_request("", "canceled"),
        lambda t: t.list_enterprise_tx_requests(""),
    ],
)
def test_tx_request_validation(client, call):
    with pytest.raises(BitGoException):
        call(TxRequest(client=client, wallet_id="w1"))
