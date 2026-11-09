from django_bitgo.resource import Resource, require


class Address(Resource):
    def list_addresses(
        self,
        coin: str = "tbtc",
        wallet_id: str = "",
        limit: int = None,
        prev_id: str = "",
        params: dict = None,
    ):
        """GET /{coin}/wallet/{walletId}/addresses"""
        query = {"limit": limit, **(params or {})}
        if prev_id:
            query["prevId"] = prev_id
        return self._get(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/addresses", params=query
        )

    def create_address(
        self, coin: str = "tbtc", wallet_id: str = "", payload: dict = None
    ):
        """POST /{coin}/wallet/{walletId}/address"""
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/address", payload=payload
        )

    def get_address(
        self,
        address_id: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        params: dict = None,
    ):
        """GET /{coin}/wallet/{walletId}/address/{addressOrId}"""
        require(address_id, "Address id")
        return self._get(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/address/{address_id}",
            params=params,
        )

    def update_address(
        self,
        address_id: str,
        payload: dict,
        coin: str = "tbtc",
        wallet_id: str = "",
    ):
        """PUT /{coin}/wallet/{walletId}/address/{addressOrId} - e.g. ``{"label": "..."}``."""
        require(address_id, "Address id")
        return self._put(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/address/{address_id}",
            payload=payload,
        )

    def list_address_balances(
        self, coin: str = "tbtc", wallet_id: str = "", params: dict = None
    ):
        """GET /{coin}/wallet/{walletId}/addresses/balances (account-based coins)."""
        return self._get(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/addresses/balances",
            params=params,
        )

    def deploy_address(
        self,
        address_id: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/address/{addressId}/deployment (forwarders)."""
        require(address_id, "Address id")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/address/{address_id}/deployment",
            payload=payload,
        )

    def forward_token(
        self,
        address_id: str,
        token_name: str,
        coin: str = "teth",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/address/{addressId}/tokenforward"""
        require(address_id, "Address id")
        require(token_name, "Token name")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/address/{address_id}/tokenforward",
            payload={**(payload or {}), "tokenName": token_name},
        )
