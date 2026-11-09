from django_bitgo.exceptions import BitGoException
from django_bitgo.resource import Resource, compact, require


class Webhook(Resource):
    """Wallet webhooks (transfer, pendingapproval, address_confirmation, ...)
    and coin-level block webhooks."""

    # --- Wallet webhooks --------------------------------------------------

    def list_wallet_webhooks(self, coin: str = "tbtc", wallet_id: str = ""):
        """GET /{coin}/wallet/{walletId}/webhooks"""
        return self._get(f"{coin}/wallet/{self._wallet_id(wallet_id)}/webhooks")

    def add_wallet_webhook(
        self,
        type: str,
        url: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/webhooks

        ``payload`` may hold ``label``, ``numConfirmations``, ``allToken``,
        ``listenToFailureStates``, ``customHttpHeaders``, ...
        """
        require(type, "Webhook type")
        require(url, "Webhook url")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/webhooks",
            payload={**(payload or {}), "type": type, "url": url},
        )

    def remove_wallet_webhook(
        self,
        type: str = None,
        url: str = None,
        webhook_id: str = None,
        coin: str = "tbtc",
        wallet_id: str = "",
    ):
        """DELETE /{coin}/wallet/{walletId}/webhooks - identify by ``webhook_id``
        or by ``type`` + ``url``."""
        if not webhook_id and not (type and url):
            raise BitGoException("Webhook id or type and url is missing but required.")
        return self._delete(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/webhooks",
            payload=compact(type=type, url=url, id=webhook_id),
        )

    def simulate_wallet_webhook(
        self,
        webhook_id: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/webhooks/{webhookId}/simulate

        ``payload`` holds ``transferId``, ``pendingApprovalId``, ``txHash`` ... depending
        on the webhook type.
        """
        require(webhook_id, "Webhook id")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/webhooks/{webhook_id}/simulate",
            payload=payload,
        )

    def list_webhook_notifications(
        self, coin: str = "tbtc", wallet_id: str = "", params: dict = None
    ):
        """GET /{coin}/wallet/{walletId}/webhooks/notifications"""
        return self._get(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/webhooks/notifications",
            params=params,
        )

    # --- Block (coin-level) webhooks --------------------------------------

    def list_block_webhooks(self, coin: str = "tbtc"):
        """GET /{coin}/webhooks"""
        return self._get(f"{coin}/webhooks")

    def add_block_webhook(
        self, url: str, coin: str = "tbtc", type: str = "block", payload=None
    ):
        """POST /{coin}/webhooks"""
        require(url, "Webhook url")
        return self._post(
            f"{coin}/webhooks", payload={**(payload or {}), "type": type, "url": url}
        )

    def remove_block_webhook(
        self,
        url: str,
        coin: str = "tbtc",
        type: str = "block",
        webhook_id: str = None,
    ):
        """DELETE /{coin}/webhooks"""
        require(url, "Webhook url")
        return self._delete(
            f"{coin}/webhooks", payload=compact(type=type, url=url, id=webhook_id)
        )

    def simulate_block_webhook(
        self, webhook_id: str, coin: str = "tbtc", block_id: str = None
    ):
        """POST /{coin}/webhooks/{webhookId}/simulate"""
        require(webhook_id, "Webhook id")
        return self._post(
            f"{coin}/webhooks/{webhook_id}/simulate", payload=compact(blockId=block_id)
        )

    # --- Notification signatures ------------------------------------------

    def create_webhook_secret(
        self, enterprise_id: str = None, organization_id: str = None
    ):
        """POST /webhook/secret - secret used to sign webhook notifications."""
        return self._post(
            "webhook/secret",
            payload=compact(enterpriseId=enterprise_id, organizationId=organization_id),
        )

    def verify_notification(
        self, webhook_id: str, notification_payload: str, signature: str
    ):
        """POST /webhook/{webhookId}/verify - asks BitGo to verify a received
        notification's signature."""
        require(webhook_id, "Webhook id")
        return self._post(
            f"webhook/{webhook_id}/verify",
            payload={
                "notificationPayload": notification_payload,
                "signature": signature,
            },
        )
