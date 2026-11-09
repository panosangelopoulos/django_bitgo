from django_bitgo.resource import Resource, compact, require


class PendingApproval(Resource):
    """Pending approvals created by wallet policies or enterprise settings."""

    def list_pending_approvals(
        self,
        wallet_id: str = None,
        enterprise_id: str = None,
        state: str = None,
        limit: int = None,
        prev_id: str = "",
        params: dict = None,
    ):
        """GET /pendingapprovals"""
        query = {
            **compact(
                walletId=wallet_id, enterpriseId=enterprise_id, state=state, limit=limit
            ),
            **(params or {}),
        }
        if prev_id:
            query["prevId"] = prev_id
        return self._get("pendingapprovals", params=query)

    def count_pending_approvals(self, params: dict = None):
        """GET /pendingapprovals/count"""
        return self._get("pendingapprovals/count", params=params)

    def get_pending_approval(self, approval_id: str, params: dict = None):
        """GET /pendingapprovals/{approvalId}"""
        require(approval_id, "Pending approval id")
        return self._get(f"pendingapprovals/{approval_id}", params=params)

    def get_pending_approval_transfer(self, approval_id: str):
        """GET /pendingapprovals/{approvalId}/transfer"""
        require(approval_id, "Pending approval id")
        return self._get(f"pendingapprovals/{approval_id}/transfer")

    def update_pending_approval(
        self,
        approval_id: str,
        state: str,
        otp: str = None,
        payload: dict = None,
    ):
        """PUT /pendingapprovals/{approvalId} - ``state`` is ``"approved"`` or ``"rejected"``.

        Approving a transaction on a self-managed (hot) wallet requires a re-signed
        ``halfSigned``/``txHex`` in ``payload``; BitGoJS/Express handle that for you.
        """
        require(approval_id, "Pending approval id")
        require(state, "State")
        return self._put(
            f"pendingapprovals/{approval_id}",
            payload={**(payload or {}), **compact(otp=otp), "state": state},
        )

    def approve(self, approval_id: str, otp: str = None, payload: dict = None):
        return self.update_pending_approval(
            approval_id, "approved", otp=otp, payload=payload
        )

    def reject(self, approval_id: str, otp: str = None, memo: str = None):
        return self.update_pending_approval(
            approval_id,
            "rejected",
            otp=otp,
            payload=compact(resolutionMemo=memo),
        )

    def bulk_update(self, approvals: list, bail_on_error: bool = None):
        """PUT /pendingapprovals/bulkupdate - ``approvals`` is a list of
        ``{"id": ..., "state": ..., "otp": ...}``."""
        require(approvals, "Approvals")
        return self._put(
            "pendingapprovals/bulkupdate",
            payload={"approvals": approvals, **compact(bailOnError=bail_on_error)},
        )
