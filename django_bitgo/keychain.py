from django_bitgo.resource import Resource, compact, require


class Keychain(Resource):
    """Keychains (public keys and encrypted private keys stored at BitGo).

    This library never generates private keys; ``add_key`` registers keys you
    generated elsewhere, while ``create_bitgo_key`` / ``create_backup_key`` ask
    BitGo (or a key recovery service) to create theirs.
    """

    def list_keys(
        self, coin: str = "tbtc", limit: int = None, prev_id: str = "", params=None
    ):
        """GET /{coin}/key"""
        query = {"limit": limit, **(params or {})}
        if prev_id:
            query["prevId"] = prev_id
        return self._get(f"{coin}/key", params=query)

    def get_key(self, key_id: str, coin: str = "tbtc"):
        """GET /{coin}/key/{id}"""
        require(key_id, "Key id")
        return self._get(f"{coin}/key/{key_id}")

    def list_wallet_keys(self, wallet_ids: list):
        """GET /keys?walletIds=... - keys for several wallets at once."""
        require(wallet_ids, "Wallet ids")
        return self._get("keys", params={"walletIds": list(wallet_ids)})

    def add_key(self, payload: dict, coin: str = "tbtc"):
        """POST /{coin}/key - e.g. ``{"pub": "xpub...", "encryptedPrv": "..."}``."""
        require(payload, "Key payload")
        return self._post(f"{coin}/key", payload=payload)

    def create_bitgo_key(
        self, coin: str = "tbtc", enterprise: str = None, payload: dict = None
    ):
        """POST /{coin}/key with ``source=bitgo`` - BitGo creates and holds its key."""
        return self._post(
            f"{coin}/key",
            payload={
                **(payload or {}),
                **compact(enterprise=enterprise),
                "source": "bitgo",
            },
        )

    def create_backup_key(
        self, coin: str = "tbtc", provider: str = None, payload: dict = None
    ):
        """POST /{coin}/key with ``source=backup`` - backup key held by a KRS provider."""
        return self._post(
            f"{coin}/key",
            payload={
                **(payload or {}),
                **compact(provider=provider),
                "source": "backup",
            },
        )

    def get_tss_pubkey(self, coin: str = "tbtc", enterprise_id: str = None):
        """GET /{coin}/tss/pubkey - BitGo's MPC public key."""
        return self._get(f"{coin}/tss/pubkey", params={"enterpriseId": enterprise_id})
