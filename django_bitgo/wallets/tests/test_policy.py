import pytest

from django_bitgo.exceptions import BitGoException
from django_bitgo.wallets.policy import Policy

RULE = {
    "id": "limit",
    "type": "velocityLimit",
    "condition": {"amountString": "1000", "timeWindow": 86400},
    "action": {"type": "getApproval"},
}


@pytest.mark.parametrize(
    "call, method",
    [
        (lambda p: p.create_rule(RULE), "POST"),
        (lambda p: p.update_rule(RULE), "PUT"),
        (lambda p: p.remove_rule(RULE), "DELETE"),
    ],
)
def test_policy_rule_endpoints(client, check_call, call, method):
    policy = Policy(client=client, wallet_id="w1")

    check_call(lambda: call(policy), method, "tbtc/wallet/w1/policy/rule", body=RULE)


def test_policy_rule_requires_id(client):
    with pytest.raises(BitGoException):
        Policy(client=client, wallet_id="w1").create_rule({"type": "x"})


def test_get_rules_reads_wallet_admin_policy(client, requests_mock):
    requests_mock.get(
        "https://app.bitgo-test.com/api/v2/tbtc/wallet/w1",
        json={"admin": {"policy": {"rules": [RULE]}}},
    )

    assert Policy(client=client, wallet_id="w1").get_rules() == [RULE]


def test_get_rules_without_policy(client, requests_mock):
    requests_mock.get("https://app.bitgo-test.com/api/v2/tbtc/wallet/w1", json={})

    assert Policy(client=client, wallet_id="w1").get_rules() == []
