import pytest

from django_bitgo.exceptions import BitGoException
from django_bitgo.pending_approval import PendingApproval


@pytest.mark.parametrize(
    "call, method, path, body, qs",
    [
        (lambda p: p.list_pending_approvals(), "GET", "pendingapprovals", None, {}),
        (
            lambda p: p.list_pending_approvals(
                wallet_id="w1", state="pending", prev_id="p1"
            ),
            "GET",
            "pendingapprovals",
            None,
            {"walletId": ["w1"], "state": ["pending"], "prevId": ["p1"]},
        ),
        (
            lambda p: p.count_pending_approvals(),
            "GET",
            "pendingapprovals/count",
            None,
            {},
        ),
        (
            lambda p: p.get_pending_approval("a1"),
            "GET",
            "pendingapprovals/a1",
            None,
            {},
        ),
        (
            lambda p: p.get_pending_approval_transfer("a1"),
            "GET",
            "pendingapprovals/a1/transfer",
            None,
            {},
        ),
        (
            lambda p: p.approve("a1", otp="000000"),
            "PUT",
            "pendingapprovals/a1",
            {"state": "approved", "otp": "000000"},
            {},
        ),
        (
            lambda p: p.reject("a1", memo="no"),
            "PUT",
            "pendingapprovals/a1",
            {"state": "rejected", "resolutionMemo": "no"},
            {},
        ),
        (
            lambda p: p.bulk_update([{"id": "a1", "state": "approved"}]),
            "PUT",
            "pendingapprovals/bulkupdate",
            {"approvals": [{"id": "a1", "state": "approved"}]},
            {},
        ),
    ],
)
def test_pending_approval_endpoints(client, check_call, call, method, path, body, qs):
    approvals = PendingApproval(client=client)

    check_call(lambda: call(approvals), method, path, body=body, qs=qs)


@pytest.mark.parametrize(
    "call",
    [
        lambda p: p.get_pending_approval(""),
        lambda p: p.update_pending_approval("a1", ""),
        lambda p: p.approve(""),
        lambda p: p.bulk_update([]),
    ],
)
def test_pending_approval_validation(client, call):
    with pytest.raises(BitGoException):
        call(PendingApproval(client=client))
