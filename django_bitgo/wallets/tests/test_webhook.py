import pytest

from django_bitgo.exceptions import BitGoException
from django_bitgo.wallets.webhook import Webhook


@pytest.mark.parametrize(
    "call, method, path, body",
    [
        (lambda h: h.list_wallet_webhooks(), "GET", "tbtc/wallet/w1/webhooks", None),
        (
            lambda h: h.add_wallet_webhook(
                "transfer", "https://x/hook", payload={"numConfirmations": 1}
            ),
            "POST",
            "tbtc/wallet/w1/webhooks",
            {"type": "transfer", "url": "https://x/hook", "numConfirmations": 1},
        ),
        (
            lambda h: h.remove_wallet_webhook(type="transfer", url="https://x/hook"),
            "DELETE",
            "tbtc/wallet/w1/webhooks",
            {"type": "transfer", "url": "https://x/hook"},
        ),
        (
            lambda h: h.remove_wallet_webhook(webhook_id="wh1"),
            "DELETE",
            "tbtc/wallet/w1/webhooks",
            {"id": "wh1"},
        ),
        (
            lambda h: h.simulate_wallet_webhook("wh1", payload={"transferId": "t1"}),
            "POST",
            "tbtc/wallet/w1/webhooks/wh1/simulate",
            {"transferId": "t1"},
        ),
        (
            lambda h: h.list_webhook_notifications(),
            "GET",
            "tbtc/wallet/w1/webhooks/notifications",
            None,
        ),
        (lambda h: h.list_block_webhooks(), "GET", "tbtc/webhooks", None),
        (
            lambda h: h.add_block_webhook("https://x/b"),
            "POST",
            "tbtc/webhooks",
            {"type": "block", "url": "https://x/b"},
        ),
        (
            lambda h: h.remove_block_webhook("https://x/b"),
            "DELETE",
            "tbtc/webhooks",
            {"type": "block", "url": "https://x/b"},
        ),
        (
            lambda h: h.simulate_block_webhook("wh1", block_id="b1"),
            "POST",
            "tbtc/webhooks/wh1/simulate",
            {"blockId": "b1"},
        ),
        (
            lambda h: h.create_webhook_secret(enterprise_id="e1"),
            "POST",
            "webhook/secret",
            {"enterpriseId": "e1"},
        ),
        (
            lambda h: h.verify_notification("wh1", "{}", "sig"),
            "POST",
            "webhook/wh1/verify",
            {"notificationPayload": "{}", "signature": "sig"},
        ),
    ],
)
def test_webhook_endpoints(client, check_call, call, method, path, body):
    webhook = Webhook(client=client, wallet_id="w1")

    check_call(lambda: call(webhook), method, path, body=body)


@pytest.mark.parametrize(
    "call",
    [
        lambda h: h.add_wallet_webhook("", "https://x"),
        lambda h: h.add_wallet_webhook("transfer", ""),
        lambda h: h.remove_wallet_webhook(type="transfer"),
        lambda h: h.simulate_wallet_webhook(""),
        lambda h: h.verify_notification("", "{}", "sig"),
    ],
)
def test_webhook_validation(client, call):
    with pytest.raises(BitGoException):
        call(Webhook(client=client, wallet_id="w1"))
