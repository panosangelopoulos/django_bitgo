from django_bitgo.resource import Resource, require


class Transfer(Resource):
    def list_transfers(
        self,
        coin: str = "tbtc",
        wallet_id: str = "",
        limit: int = 25,
        prev_id: str = "",
        all_tokens: bool = False,
        params: dict = None,
    ):
        """GET /{coin}/wallet/{walletId}/transfer - filter with ``params``
        (``state``, ``type``, ``dateGte``, ``address``, ...)."""
        query = {"limit": limit, "allTokens": all_tokens, **(params or {})}
        if prev_id:
            query["prevId"] = prev_id
        return self._get(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/transfer", params=query
        )

    def get_transfer(self, transfer_id: str, coin: str = "tbtc", wallet_id: str = ""):
        """GET /{coin}/wallet/{walletId}/transfer/{transferId}"""
        wallet_id = self._wallet_id(wallet_id)
        require(transfer_id, "Transfer id")
        return self._get(f"{coin}/wallet/{wallet_id}/transfer/{transfer_id}")

    def get_transfer_by_sequence_id(
        self, sequence_id: str, coin: str = "tbtc", wallet_id: str = ""
    ):
        """GET /{coin}/wallet/{walletId}/transfer/sequenceId/{sequenceId}"""
        wallet_id = self._wallet_id(wallet_id)
        require(sequence_id, "Sequence id")
        return self._get(f"{coin}/wallet/{wallet_id}/transfer/sequenceId/{sequence_id}")

    def comment_transfer(
        self, transfer_id: str, comment: str, coin: str = "tbtc", wallet_id: str = ""
    ):
        """POST /{coin}/wallet/{walletId}/transfer/{transferId}/comment"""
        wallet_id = self._wallet_id(wallet_id)
        require(transfer_id, "Transfer id")
        return self._post(
            f"{coin}/wallet/{wallet_id}/transfer/{transfer_id}/comment",
            payload={"comment": comment},
        )

    def list_enterprise_transfers(
        self,
        enterprise_id: str,
        limit: int = 25,
        prev_id: str = "",
        params: dict = None,
    ):
        """GET /enterprise/{enterpriseId}/transfer"""
        require(enterprise_id, "Enterprise id")
        query = {"limit": limit, **(params or {})}
        if prev_id:
            query["prevId"] = prev_id
        return self._get(f"enterprise/{enterprise_id}/transfer", params=query)

    def get_fee_estimate(
        self, coin: str = "tbtc", num_blocks: int = None, params: dict = None
    ):
        """GET /{coin}/tx/fee - current fee rate estimate."""
        return self._get(
            f"{coin}/tx/fee", params={"numBlocks": num_blocks, **(params or {})}
        )

    def get_transaction(self, tx_id: str, coin: str = "tbtc"):
        """GET /{coin}/tx/{txId}"""
        require(tx_id, "Transaction id")
        return self._get(f"{coin}/tx/{tx_id}")
