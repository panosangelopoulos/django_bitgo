from django_bitgo.client import BitGoClient
from django_bitgo.exceptions import BitGoException


class Transfer:
    def __init__(self, client: BitGoClient = None, wallet_id: str = "") -> None:
        self.client = client or BitGoClient()
        self.wallet_id = wallet_id

    def list_transfers(
        self,
        coin: str = "tbtc",
        wallet_id: str = "",
        limit: int = 25,
        prev_id: str = "",
        all_tokens: bool = False,
    ):
        wallet_id = wallet_id or self.wallet_id
        if not wallet_id:
            raise BitGoException("Wallet id is missing but required.")

        params = {"limit": limit, "allTokens": all_tokens}
        if prev_id:
            params["prevId"] = prev_id

        response = self.client.request(
            method="GET", path=f"{coin}/wallet/{wallet_id}/transfer", params=params
        )
        return response.json()

    def get_transfer(self, transfer_id: str, coin: str = "tbtc", wallet_id: str = ""):
        wallet_id = wallet_id or self.wallet_id
        if not wallet_id:
            raise BitGoException("Wallet id is missing but required.")
        if not transfer_id:
            raise BitGoException("Transfer id is missing but required.")

        response = self.client.request(
            method="GET",
            path=f"{coin}/wallet/{wallet_id}/transfer/{transfer_id}",
        )
        return response.json()
