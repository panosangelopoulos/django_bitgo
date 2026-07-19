from django_bitgo.client import BitGoClient
from django_bitgo.exceptions import BitGoException


class Wallet:
    def __init__(self, client: BitGoClient = None, wallet_id: str = "") -> None:
        self.client = client or BitGoClient()
        self.wallet_id = wallet_id

    def list_wallets(
        self,
        coin: str = "tbtc",
        limit: int = 25,
        prev_id: str = "",
        all_tokens: bool = False,
    ):
        params = {"limit": limit, "allTokens": all_tokens}
        if prev_id:
            params["prevId"] = prev_id

        response = self.client.request(
            method="GET", path=f"{coin}/wallet", params=params
        )
        return response.json()

    def get_wallet(self, wallet_id: str = "", coin: str = "tbtc"):
        wallet_id = wallet_id or self.wallet_id
        if not wallet_id:
            raise BitGoException("Wallet id is missing but required.")

        response = self.client.request(method="GET", path=f"{coin}/wallet/{wallet_id}")
        return response.json()

    def create_wallet(self, coin: str = "tbtc", payload: dict = None):
        # Registers a wallet with pre-generated keys (BitGo's "add wallet" endpoint);
        # this library does not generate or custody keys, payload must include them.
        response = self.client.request(
            method="POST", path=f"{coin}/wallet/add", payload=payload
        )
        return response.json()
