from django_bitgo.resource import Resource, require


class WalletShare(Resource):
    """Wallet sharing.

    Sharing *spend* access requires encrypting the user key for the recipient;
    use ``Express.share_wallet`` / ``Express.accept_share`` for that. The REST
    methods here cover view/admin shares and share management.
    """

    def list_shares(self):
        """GET /walletshares - incoming and outgoing shares."""
        return self._get("walletshares")

    def count_shares(self, state: str):
        """GET /walletshares/count"""
        require(state, "State")
        return self._get("walletshares/count", params={"state": state})

    def get_share(self, share_id: str, coin: str = "tbtc"):
        """GET /{coin}/walletshare/{shareId}"""
        require(share_id, "Share id")
        return self._get(f"{coin}/walletshare/{share_id}")

    def create_share(
        self,
        user: str,
        permission: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/share

        ``user`` is the recipient's user id, ``permission`` a comma-separated list
        (``"view"``, ``"view,spend"``, ``"admin,spend,view"``).
        """
        require(user, "User")
        require(permission, "Permission")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/share",
            payload={**(payload or {}), "user": user, "permission": permission},
        )

    def update_share(
        self, share_id: str, state: str, coin: str = "tbtc", payload: dict = None
    ):
        """POST /{coin}/walletshare/{shareId} - ``state`` is ``"accepted"`` or ``"rejected"``."""
        require(share_id, "Share id")
        require(state, "State")
        return self._post(
            f"{coin}/walletshare/{share_id}",
            payload={**(payload or {}), "state": state},
        )

    def accept_share(self, share_id: str, coin: str = "tbtc", payload: dict = None):
        """Accepts a view-only share (spend shares: use ``Express.accept_share``)."""
        return self.update_share(share_id, "accepted", coin=coin, payload=payload)

    def reject_share(self, share_id: str, coin: str = "tbtc"):
        return self.update_share(share_id, "rejected", coin=coin)

    def cancel_share(self, share_id: str, coin: str = "tbtc"):
        """DELETE /{coin}/walletshare/{shareId} - cancel outgoing or reject incoming."""
        require(share_id, "Share id")
        return self._delete(f"{coin}/walletshare/{share_id}")

    def resend_share_email(self, share_id: str, coin: str = "tbtc"):
        """POST /{coin}/walletshare/{shareId}/resendemail"""
        require(share_id, "Share id")
        return self._post(f"{coin}/walletshare/{share_id}/resendemail")
