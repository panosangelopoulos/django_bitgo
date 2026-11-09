import pytest

from django_bitgo.enterprise import Enterprise
from django_bitgo.exceptions import BitGoException


@pytest.mark.parametrize(
    "call, method, path, body",
    [
        (lambda e: e.list_enterprises(), "GET", "enterprise", None),
        (lambda e: e.get_enterprise("e1"), "GET", "enterprise/e1", None),
        (
            lambda e: e.update_enterprise("e1", {"approvalsRequired": 2}),
            "PUT",
            "enterprise/e1",
            {"approvalsRequired": 2},
        ),
        (
            lambda e: e.get_fee_address_balance("e1"),
            "GET",
            "teth/enterprise/e1/feeAddressBalance",
            None,
        ),
        (
            lambda e: e.get_wallet_limits("e1"),
            "GET",
            "enterprise/e1/walletLimits",
            None,
        ),
        (
            lambda e: e.list_available_assets("e1"),
            "GET",
            "enterprise/e1/availableassets",
            None,
        ),
        (
            lambda e: e.add_user("e1", "a@b.c", permission="admin"),
            "POST",
            "enterprise/e1/user",
            {"username": "a@b.c", "permission": "admin"},
        ),
        (
            lambda e: e.update_user("e1", {"username": "a@b.c"}),
            "PUT",
            "enterprise/e1/user",
            {"username": "a@b.c"},
        ),
        (
            lambda e: e.remove_user("e1", "a@b.c"),
            "DELETE",
            "enterprise/e1/user",
            {"username": "a@b.c"},
        ),
        (lambda e: e.list_webhooks("e1"), "GET", "enterprise/e1/webhooks", None),
        (
            lambda e: e.add_webhook("e1", {"type": "accessToken", "url": "u"}),
            "POST",
            "enterprise/e1/webhooks",
            {"type": "accessToken", "url": "u"},
        ),
        (
            lambda e: e.remove_webhook("e1", "wh1"),
            "DELETE",
            "enterprise/e1/webhook/wh1",
            None,
        ),
        (
            lambda e: e.simulate_webhook("e1", "wh1"),
            "GET",
            "enterprise/e1/webhook/wh1/simulate",
            None,
        ),
    ],
)
def test_enterprise_endpoints(client, check_call, call, method, path, body):
    check_call(lambda: call(Enterprise(client=client)), method, path, body=body)


@pytest.mark.parametrize(
    "call",
    [
        lambda e: e.get_enterprise(""),
        lambda e: e.add_user("e1", ""),
        lambda e: e.remove_webhook("e1", ""),
    ],
)
def test_enterprise_validation(client, call):
    with pytest.raises(BitGoException):
        call(Enterprise(client=client))
