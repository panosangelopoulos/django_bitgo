from django_bitgo.resource import Resource, require


class TxRequest(Resource):
    """Transaction requests (the flow used by TSS/MPC and custodial wallets).

    Signing itself (commitments, signature shares) must happen client-side with
    the user key, typically via BitGo Express or BitGoJS; this class covers
    creating, listing and cancelling requests.
    """

    def list_tx_requests(self, wallet_id: str = "", params: dict = None):
        """GET /wallet/{walletId}/txrequests - filter with ``txRequestIds``, ``states``, ..."""
        return self._get(
            f"wallet/{self._wallet_id(wallet_id)}/txrequests", params=params
        )

    def get_tx_request(self, tx_request_id: str, wallet_id: str = ""):
        """Fetches the latest version of a single transaction request."""
        require(tx_request_id, "Transaction request id")
        result = self.list_tx_requests(
            wallet_id=wallet_id,
            params={"txRequestIds": tx_request_id, "latest": True},
        )
        requests = result.get("txRequests") or []
        return requests[0] if requests else None

    def create_tx_request(
        self,
        intent: dict,
        wallet_id: str = "",
        api_version: str = "full",
        payload: dict = None,
    ):
        """POST /wallet/{walletId}/txrequests

        ``intent`` e.g. ``{"intentType": "payment", "recipients": [...]}``.
        """
        require(intent, "Intent")
        return self._post(
            f"wallet/{self._wallet_id(wallet_id)}/txrequests",
            payload={**(payload or {}), "intent": intent, "apiVersion": api_version},
        )

    def update_tx_request(
        self,
        tx_request_id: str,
        state: str,
        wallet_id: str = "",
        cancellation_reason: str = None,
    ):
        """PUT /wallet/{walletId}/txrequests/{txRequestId}"""
        require(tx_request_id, "Transaction request id")
        require(state, "State")
        payload = {"state": state}
        if cancellation_reason:
            payload["cancellationReason"] = cancellation_reason
        return self._put(
            f"wallet/{self._wallet_id(wallet_id)}/txrequests/{tx_request_id}",
            payload=payload,
        )

    def cancel_tx_request(
        self, tx_request_id: str, wallet_id: str = "", reason: str = None
    ):
        return self.update_tx_request(
            tx_request_id, "canceled", wallet_id=wallet_id, cancellation_reason=reason
        )

    def list_awaiting_signature(self, wallet_id: str = "", params: dict = None):
        """GET /wallet/{walletId}/txrequests/awaitingsignature"""
        return self._get(
            f"wallet/{self._wallet_id(wallet_id)}/txrequests/awaitingsignature",
            params=params,
        )

    def list_enterprise_tx_requests(self, enterprise_id: str, params: dict = None):
        """GET /enterprise/{enterpriseId}/txrequests"""
        require(enterprise_id, "Enterprise id")
        return self._get(f"enterprise/{enterprise_id}/txrequests", params=params)
