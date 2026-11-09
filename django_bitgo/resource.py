from django.conf import settings

from django_bitgo.client import BitGoClient
from django_bitgo.exceptions import BitGoException


def require(value, name: str):
    if not value:
        raise BitGoException(f"{name} is missing but required.")
    return value


def compact(**fields) -> dict:
    """Builds a dict from keyword arguments, dropping ``None`` values."""
    return {key: value for key, value in fields.items() if value is not None}


class Resource:
    """Base class for BitGo API resources."""

    client_class = BitGoClient

    def __init__(self, client: BitGoClient = None, wallet_id: str = "") -> None:
        self.client = client or self.client_class()
        self.wallet_id = wallet_id or getattr(settings, "BITGO_WALLET_ID", None) or ""

    def _wallet_id(self, wallet_id: str = "") -> str:
        return require(wallet_id or self.wallet_id, "Wallet id")

    def _request(self, method: str, path: str, payload=None, params=None):
        response = self.client.request(
            method=method, path=path, payload=payload, params=params
        )
        if not response.content:
            return {}
        return response.json()

    def _get(self, path: str, params=None):
        return self._request("GET", path, params=params)

    def _post(self, path: str, payload=None, params=None):
        return self._request("POST", path, payload=payload, params=params)

    def _put(self, path: str, payload=None, params=None):
        return self._request("PUT", path, payload=payload, params=params)

    def _patch(self, path: str, payload=None):
        return self._request("PATCH", path, payload=payload)

    def _delete(self, path: str, payload=None, params=None):
        return self._request("DELETE", path, payload=payload, params=params)


def iter_pages(method, *args, **kwargs):
    """
    Follows BitGo's ``nextBatchPrevId`` cursor and yields each page.

    ``method`` must be a list method accepting a ``prev_id`` keyword, e.g.::

        for page in iter_pages(Wallet().list_wallets, coin="tbtc"):
            for wallet in page["wallets"]:
                ...
    """
    prev_id = kwargs.pop("prev_id", "")
    while True:
        page = method(*args, prev_id=prev_id, **kwargs)
        yield page
        prev_id = page.get("nextBatchPrevId") if isinstance(page, dict) else None
        if not prev_id:
            return
