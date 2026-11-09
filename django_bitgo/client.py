import requests
import os
from django.conf import settings

from django_bitgo.exceptions import BitGoException

DEFAULT_EXPRESS_URL = "http://localhost:3080/"


def _normalize_params(params):
    # BitGo validates boolean query params as the strings "true"/"false";
    # requests would otherwise send Python's "True"/"False". None values are dropped.
    if not params:
        return None
    normalized = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            value = "true" if value else "false"
        normalized[key] = value
    return normalized or None


class BitGoClient(object):
    def __init__(
        self, access_token: str = "", api_url: str = "", timeout: float = None
    ) -> None:
        """
        Initializes the BitGo Client

        :param str access_token: Access Token to authenticate with
        :param str api_url: Overrides ``settings.BITGO_API_URL`` (e.g. to target BitGo Express)
        :param float timeout: Optional requests timeout in seconds
        """

        self.access_token = access_token or os.getenv("BITGO_ACCESS_TOKEN")
        self.api_url = api_url
        self.timeout = timeout

        if not self.access_token:
            raise BitGoException("Access token is required to create a BitGoClient")

    def request(self, method="GET", headers=None, path="", payload=None, params=None):
        headers = {**(headers or {}), "Authorization": f"Bearer {self.access_token}"}

        try:
            response = requests.request(
                method=method,
                url=f"{self.get_api_url()}{self.get_api_version()}{path}",
                headers=headers,
                json=payload or None,
                params=_normalize_params(params),
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as e:
            raise BitGoException(f"A connection error raised! {str(e)}")

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise self._build_http_exception(response, e) from e

        return response

    @staticmethod
    def _build_http_exception(response, error):
        try:
            body = response.json()
        except ValueError:
            body = None

        error_name = request_id = detail = None
        if isinstance(body, dict):
            error_name = body.get("name")
            request_id = body.get("requestId")
            detail = body.get("error") or body.get("message")

        message = f"BitGo API returned an error: {str(error)}"
        if detail:
            message = f"{message} - {detail}"

        return BitGoException(
            message,
            status_code=response.status_code,
            error_name=error_name,
            request_id=request_id,
            response_body=body,
        )

    def get_api_url(self):
        return self.api_url or settings.BITGO_API_URL

    def get_api_version(self):
        return settings.BITGO_API_VERSION


class ExpressClient(BitGoClient):
    """
    Client for a BitGo Express instance (BitGo's self-hosted signing server).

    Express is required for anything that signs with a user key: sending coins,
    generating wallets, accelerating/consolidating transactions, accepting shares.
    It defaults to ``settings.BITGO_EXPRESS_URL`` or ``http://localhost:3080/``.
    """

    def __init__(
        self, access_token: str = "", api_url: str = "", timeout: float = None
    ) -> None:
        super().__init__(
            access_token=access_token,
            api_url=api_url
            or getattr(settings, "BITGO_EXPRESS_URL", None)
            or DEFAULT_EXPRESS_URL,
            timeout=timeout,
        )
