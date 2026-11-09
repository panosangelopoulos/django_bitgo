from django_bitgo.resource import Resource, require


class Wallet(Resource):
    # --- Listing / lookup -------------------------------------------------

    def list_wallets(
        self,
        coin: str = "tbtc",
        limit: int = 25,
        prev_id: str = "",
        all_tokens: bool = False,
        params: dict = None,
    ):
        """GET /{coin}/wallet - wallets of a single coin."""
        query = {"limit": limit, "allTokens": all_tokens, **(params or {})}
        if prev_id:
            query["prevId"] = prev_id
        return self._get(f"{coin}/wallet", params=query)

    def list_all_wallets(self, limit: int = 25, prev_id: str = "", params=None):
        """GET /wallets - wallets across all coins (filter with ``params``)."""
        query = {"limit": limit, **(params or {})}
        if prev_id:
            query["prevId"] = prev_id
        return self._get("wallets", params=query)

    def count_wallets(self, params: dict = None):
        """GET /wallets/count"""
        return self._get("wallets/count", params=params)

    def get_wallet(self, wallet_id: str = "", coin: str = "tbtc", params=None):
        """GET /{coin}/wallet/{walletId}"""
        return self._get(f"{coin}/wallet/{self._wallet_id(wallet_id)}", params=params)

    def get_wallet_by_id(self, wallet_id: str = "", params: dict = None):
        """GET /wallet/{walletId} - lookup without knowing the coin."""
        return self._get(f"wallet/{self._wallet_id(wallet_id)}", params=params)

    def get_wallet_by_address(self, address: str, coin: str = "tbtc"):
        """GET /{coin}/wallet/address/{address}"""
        require(address, "Address")
        return self._get(f"{coin}/wallet/address/{address}")

    # --- Create / update / delete -----------------------------------------

    def create_wallet(self, coin: str = "tbtc", payload: dict = None):
        """POST /{coin}/wallet/add

        Registers a wallet with pre-generated keys (BitGo's "add wallet" endpoint);
        this library does not generate or custody keys, payload must include them.
        To have keys generated, use ``Express.generate_wallet``.
        """
        return self._post(f"{coin}/wallet/add", payload=payload)

    def update_wallet(self, payload: dict, wallet_id: str = "", coin: str = "tbtc"):
        """PUT /{coin}/wallet/{walletId} - e.g. ``{"label": "..."}``."""
        return self._put(f"{coin}/wallet/{self._wallet_id(wallet_id)}", payload=payload)

    def remove_wallet(self, wallet_id: str = "", coin: str = "tbtc"):
        """DELETE /{coin}/wallet/{walletId} - only allowed for empty wallets."""
        return self._delete(f"{coin}/wallet/{self._wallet_id(wallet_id)}")

    def remove_user(self, user_id: str, wallet_id: str = "", coin: str = "tbtc"):
        """DELETE /{coin}/wallet/{walletId}/user/{userId}"""
        require(user_id, "User id")
        return self._delete(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/user/{user_id}"
        )

    def freeze_wallet(
        self,
        duration: int,
        wallet_id: str = "",
        coin: str = "tbtc",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/freeze - blocks spending for ``duration`` seconds."""
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/freeze",
            payload={**(payload or {}), "duration": duration},
        )

    # --- Balances / unspents ----------------------------------------------

    def get_total_balances(self, coin: str = "", params: dict = None):
        """GET /{coin}/wallet/balances, or /wallet/balances when ``coin`` is empty."""
        path = f"{coin}/wallet/balances" if coin else "wallet/balances"
        return self._get(path, params=params)

    def get_maximum_spendable(
        self, wallet_id: str = "", coin: str = "tbtc", params: dict = None
    ):
        """GET /{coin}/wallet/{walletId}/maximumSpendable"""
        return self._get(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/maximumSpendable",
            params=params,
        )

    def list_unspents(
        self,
        wallet_id: str = "",
        coin: str = "tbtc",
        limit: int = 25,
        prev_id: str = "",
        params: dict = None,
    ):
        """GET /{coin}/wallet/{walletId}/unspents (UTXO coins only)."""
        query = {"limit": limit, **(params or {})}
        if prev_id:
            query["prevId"] = prev_id
        return self._get(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/unspents", params=query
        )

    # --- Transactions -----------------------------------------------------

    def build_transaction(self, payload: dict, wallet_id: str = "", coin: str = "tbtc"):
        """POST /{coin}/wallet/{walletId}/tx/build - unsigned prebuild, e.g.
        ``{"recipients": [{"address": "...", "amount": "1000"}]}``."""
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/tx/build", payload=payload
        )

    def send_transaction(self, payload: dict, wallet_id: str = "", coin: str = "tbtc"):
        """POST /{coin}/wallet/{walletId}/tx/send - submits a half-signed transaction
        (``{"halfSigned": {"txHex": "..."}}``) for BitGo to co-sign and broadcast."""
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/tx/send", payload=payload
        )

    def initiate_transaction(
        self, payload: dict, wallet_id: str = "", coin: str = "tbtc"
    ):
        """POST /{coin}/wallet/{walletId}/tx/initiate - custodial wallets only."""
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/tx/initiate", payload=payload
        )

    def change_fee(
        self,
        txid: str,
        wallet_id: str = "",
        coin: str = "tbtc",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/tx/changeFee - bump a stuck account-based tx."""
        require(txid, "Transaction id")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/tx/changeFee",
            payload={**(payload or {}), "txid": txid},
        )

    def build_consolidate_unspents(
        self, wallet_id: str = "", coin: str = "tbtc", payload: dict = None
    ):
        """POST /{coin}/wallet/{walletId}/consolidateUnspents - builds (does not sign)
        a consolidation. To build, sign and send in one call use
        ``Express.consolidate_unspents``."""
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/consolidateUnspents",
            payload=payload,
        )

    def build_consolidate_account(
        self, wallet_id: str = "", coin: str = "tbtc", payload: dict = None
    ):
        """POST /{coin}/wallet/{walletId}/consolidateAccount/build - account-based coins."""
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/consolidateAccount/build",
            payload=payload,
        )
