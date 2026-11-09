from django_bitgo.client import ExpressClient
from django_bitgo.exceptions import BitGoException
from django_bitgo.resource import Resource, compact, require


class Express(Resource):
    """Operations that must run through BitGo Express.

    Express is BitGo's self-hosted signing server: it decrypts the user key with
    the wallet passphrase locally, signs, and forwards to BitGo. Run it with e.g.
    ``docker run -p 3080:3080 bitgo/express:latest`` and point
    ``settings.BITGO_EXPRESS_URL`` at it (default ``http://localhost:3080/``).
    """

    client_class = ExpressClient

    def ping(self):
        """GET /pingexpress"""
        return self._get("pingexpress")

    # --- Wallets ----------------------------------------------------------

    def generate_wallet(
        self,
        label: str,
        enterprise: str,
        passphrase: str = None,
        coin: str = "tbtc",
        include_keychains: bool = None,
        payload: dict = None,
    ):
        """POST /{coin}/wallet/generate - creates user/backup/BitGo keys and the wallet.

        The response contains the encrypted user keychain; back it up.
        """
        require(label, "Label")
        require(enterprise, "Enterprise")
        return self._post(
            f"{coin}/wallet/generate",
            payload={
                **(payload or {}),
                **compact(passphrase=passphrase),
                "label": label,
                "enterprise": enterprise,
            },
            params={"includeKeychains": include_keychains},
        )

    def share_wallet(
        self,
        email: str,
        permissions: str,
        wallet_passphrase: str = None,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/share - ``wallet_passphrase`` is needed
        when sharing ``spend``."""
        require(email, "Email")
        require(permissions, "Permissions")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/share",
            payload={
                **(payload or {}),
                **compact(walletPassphrase=wallet_passphrase),
                "email": email,
                "permissions": permissions,
            },
        )

    def accept_share(
        self,
        share_id: str,
        user_password: str = None,
        new_wallet_passphrase: str = None,
        coin: str = "tbtc",
        payload: dict = None,
    ):
        """POST /{coin}/walletshare/{shareId}/acceptshare"""
        require(share_id, "Share id")
        return self._post(
            f"{coin}/walletshare/{share_id}/acceptshare",
            payload={
                **(payload or {}),
                **compact(
                    userPassword=user_password,
                    newWalletPassphrase=new_wallet_passphrase,
                ),
            },
        )

    # --- Sending ----------------------------------------------------------

    def send_coins(
        self,
        address: str,
        amount,
        wallet_passphrase: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/sendcoins

        ``amount`` is in base units (satoshi, wei, ...); pass it as a string for
        large values. ``payload`` takes ``feeRate``, ``comment``, ``sequenceId``,
        ``otp``, ...  A 202 response means the send is awaiting approval.
        """
        require(address, "Address")
        require(amount, "Amount")
        require(wallet_passphrase, "Wallet passphrase")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/sendcoins",
            payload={
                **(payload or {}),
                "address": address,
                "amount": amount,
                "walletPassphrase": wallet_passphrase,
            },
        )

    def send_many(
        self,
        recipients: list,
        wallet_passphrase: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/sendmany - ``recipients`` is a list of
        ``{"address": ..., "amount": ...}``."""
        require(recipients, "Recipients")
        require(wallet_passphrase, "Wallet passphrase")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/sendmany",
            payload={
                **(payload or {}),
                "recipients": recipients,
                "walletPassphrase": wallet_passphrase,
            },
        )

    def sign_transaction(self, payload: dict, coin: str = "tbtc", wallet_id: str = ""):
        """POST /{coin}/wallet/{walletId}/signtx - signs a prebuild
        (``{"txPrebuild": ..., "walletPassphrase": ...}``)."""
        require(payload, "Payload")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/signtx", payload=payload
        )

    def sign_tss_transaction(
        self, payload: dict, coin: str = "tbtc", wallet_id: str = ""
    ):
        """POST /{coin}/wallet/{walletId}/signtxtss - signs a TSS transaction request."""
        require(payload, "Payload")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/signtxtss", payload=payload
        )

    def accelerate_transaction(
        self,
        wallet_passphrase: str,
        cpfp_tx_ids: list = None,
        rbf_tx_ids: list = None,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/acceleratetx - CPFP or RBF a stuck tx."""
        require(wallet_passphrase, "Wallet passphrase")
        if not cpfp_tx_ids and not rbf_tx_ids:
            raise BitGoException("cpfp_tx_ids or rbf_tx_ids is missing but required.")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/acceleratetx",
            payload={
                **(payload or {}),
                **compact(cpfpTxIds=cpfp_tx_ids, rbfTxIds=rbf_tx_ids),
                "walletPassphrase": wallet_passphrase,
            },
        )

    # --- Unspent management -----------------------------------------------

    def consolidate_unspents(
        self,
        wallet_passphrase: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/consolidateunspents"""
        return self._wallet_op(
            "consolidateunspents", wallet_passphrase, coin, wallet_id, payload
        )

    def fanout_unspents(
        self,
        wallet_passphrase: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/fanoutunspents"""
        return self._wallet_op(
            "fanoutunspents", wallet_passphrase, coin, wallet_id, payload
        )

    def consolidate_account(
        self,
        wallet_passphrase: str,
        coin: str = "teth",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/consolidateAccount (account-based coins)."""
        return self._wallet_op(
            "consolidateAccount", wallet_passphrase, coin, wallet_id, payload
        )

    def sweep(
        self,
        address: str,
        wallet_passphrase: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/sweep - sends the whole balance to ``address``."""
        require(address, "Address")
        return self._wallet_op(
            "sweep",
            wallet_passphrase,
            coin,
            wallet_id,
            {**(payload or {}), "address": address},
        )

    # --- Addresses --------------------------------------------------------

    def verify_address(self, address: str, coin: str = "tbtc"):
        """POST /{coin}/verifyaddress - checks the address is valid for ``coin``."""
        require(address, "Address")
        return self._post(f"{coin}/verifyaddress", payload={"address": address})

    def canonical_address(self, address: str, coin: str = "tbch", version=None):
        """POST /{coin}/canonicaladdress (e.g. BCH legacy <-> cashaddr)."""
        require(address, "Address")
        return self._post(
            f"{coin}/canonicaladdress",
            payload=compact(address=address, version=version),
        )

    def is_wallet_address(
        self,
        address: str,
        keychains: list,
        coin: str = "teth",
        wallet_id: str = "",
        payload: dict = None,
    ):
        """POST /{coin}/wallet/{walletId}/iswalletaddress"""
        require(address, "Address")
        require(keychains, "Keychains")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/iswalletaddress",
            payload={**(payload or {}), "address": address, "keychains": keychains},
        )

    def _wallet_op(self, op, wallet_passphrase, coin, wallet_id, payload):
        require(wallet_passphrase, "Wallet passphrase")
        return self._post(
            f"{coin}/wallet/{self._wallet_id(wallet_id)}/{op}",
            payload={**(payload or {}), "walletPassphrase": wallet_passphrase},
        )
