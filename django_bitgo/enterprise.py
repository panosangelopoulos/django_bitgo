from django_bitgo.resource import Resource, compact, require


class Enterprise(Resource):
    def list_enterprises(self, params: dict = None):
        """GET /enterprise"""
        return self._get("enterprise", params=params)

    def get_enterprise(self, enterprise_id: str, params: dict = None):
        """GET /enterprise/{enterpriseId}"""
        require(enterprise_id, "Enterprise id")
        return self._get(f"enterprise/{enterprise_id}", params=params)

    def update_enterprise(self, enterprise_id: str, payload: dict):
        """PUT /enterprise/{enterpriseId}"""
        require(enterprise_id, "Enterprise id")
        return self._put(f"enterprise/{enterprise_id}", payload=payload)

    def get_fee_address_balance(self, enterprise_id: str, coin: str = "teth"):
        """GET /{coin}/enterprise/{enterpriseId}/feeAddressBalance (gas tank)."""
        require(enterprise_id, "Enterprise id")
        return self._get(f"{coin}/enterprise/{enterprise_id}/feeAddressBalance")

    def get_wallet_limits(self, enterprise_id: str, params: dict = None):
        """GET /enterprise/{enterpriseId}/walletLimits"""
        require(enterprise_id, "Enterprise id")
        return self._get(f"enterprise/{enterprise_id}/walletLimits", params=params)

    def list_available_assets(self, enterprise_id: str, params: dict = None):
        """GET /enterprise/{enterpriseId}/availableassets"""
        require(enterprise_id, "Enterprise id")
        return self._get(f"enterprise/{enterprise_id}/availableassets", params=params)

    # --- Users ------------------------------------------------------------

    def add_user(
        self,
        enterprise_id: str,
        username: str,
        permission: str = None,
        payload: dict = None,
    ):
        """POST /enterprise/{enterpriseId}/user"""
        require(enterprise_id, "Enterprise id")
        require(username, "Username")
        return self._post(
            f"enterprise/{enterprise_id}/user",
            payload={
                **(payload or {}),
                **compact(permission=permission),
                "username": username,
            },
        )

    def update_user(self, enterprise_id: str, payload: dict):
        """PUT /enterprise/{enterpriseId}/user"""
        require(enterprise_id, "Enterprise id")
        return self._put(f"enterprise/{enterprise_id}/user", payload=payload)

    def remove_user(self, enterprise_id: str, username: str):
        """DELETE /enterprise/{enterpriseId}/user"""
        require(enterprise_id, "Enterprise id")
        require(username, "Username")
        return self._delete(
            f"enterprise/{enterprise_id}/user", payload={"username": username}
        )

    # --- Enterprise webhooks ----------------------------------------------

    def list_webhooks(self, enterprise_id: str):
        """GET /enterprise/{enterpriseId}/webhooks"""
        require(enterprise_id, "Enterprise id")
        return self._get(f"enterprise/{enterprise_id}/webhooks")

    def add_webhook(self, enterprise_id: str, payload: dict):
        """POST /enterprise/{enterpriseId}/webhooks"""
        require(enterprise_id, "Enterprise id")
        return self._post(f"enterprise/{enterprise_id}/webhooks", payload=payload)

    def remove_webhook(self, enterprise_id: str, webhook_id: str):
        """DELETE /enterprise/{enterpriseId}/webhook/{webhookId}"""
        require(enterprise_id, "Enterprise id")
        require(webhook_id, "Webhook id")
        return self._delete(f"enterprise/{enterprise_id}/webhook/{webhook_id}")

    def simulate_webhook(self, enterprise_id: str, webhook_id: str):
        """GET /enterprise/{enterpriseId}/webhook/{webhookId}/simulate"""
        require(enterprise_id, "Enterprise id")
        require(webhook_id, "Webhook id")
        return self._get(f"enterprise/{enterprise_id}/webhook/{webhook_id}/simulate")
