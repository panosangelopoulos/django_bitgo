from django.conf import settings

from django_bitgo.client import BitGoClient
from django_bitgo.exceptions import BitGoException


class Address:
    def __init__(self, client: BitGoClient = None, wallet_id: str = "") -> None:
        self.client = client or BitGoClient()
        self.wallet_id = wallet_id or settings.BITGO_WALLET_ID

    def list_addresses(self, coin: str = "tbtc", wallet_id: str = ""):
        response = self.client.request(
            method="GET",
            path=f"{coin}/wallet/{wallet_id or self.wallet_id}/addresses",
        )
        return response.json()

    def create_address(
        self, coin: str = "tbtc", wallet_id: str = "", payload: dict = None
    ):
        response = self.client.request(
            method="POST",
            path=f"{coin}/wallet/{wallet_id or self.wallet_id}/address",
            payload=payload,
        )
        return response.json()

    def deploy_address(
        self,
        address_id: str,
        coin: str = "tbtc",
        wallet_id: str = "",
        payload: dict = None,
    ):
        if not address_id:
            raise BitGoException("Address id is missing but required.")

        response = self.client.request(
            method="POST",
            path=f"{coin}/wallet/{wallet_id or self.wallet_id}/address/{address_id}/deployment",
            payload=payload,
        )
        return response.json()

    def get_address(self, address_id: str, coin: str = "tbtc", wallet_id: str = ""):
        if not address_id:
            raise BitGoException("Address id is missing but required.")

        response = self.client.request(
            method="GET",
            path=f"{coin}/wallet/{wallet_id or self.wallet_id}/address/{address_id}",
        )
        return response.json()
