import os

import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_bitgo.settings_testing_locally")


@pytest.fixture(autouse=True)
def bitgo_settings(monkeypatch):
    # Keep tests independent of a developer's local BITGO_* environment.
    from django.conf import settings

    monkeypatch.setattr(settings, "BITGO_API_URL", "https://app.bitgo-test.com/")
    monkeypatch.setattr(settings, "BITGO_API_VERSION", "api/v2/")
    monkeypatch.setattr(settings, "BITGO_EXPRESS_URL", "http://localhost:3080/")
    monkeypatch.setattr(settings, "BITGO_WALLET_ID", None)
    return settings


_UNSET = object()


@pytest.fixture
def client():
    from django_bitgo.client import BitGoClient

    return BitGoClient(access_token="my-token")


@pytest.fixture
def check_call(requests_mock):
    """
    Registers ``method base+path``, runs ``call`` and asserts on the exact request.

    ``body`` is compared to the JSON body (``None`` asserts no body was sent);
    ``qs`` is compared to the raw (case-preserving) query string dict.
    """
    from urllib.parse import parse_qs, urlparse

    def check(
        call,
        method,
        path,
        body=_UNSET,
        qs=_UNSET,
        base="https://app.bitgo-test.com/api/v2/",
        response=None,
    ):
        response = {"ok": True} if response is None else response
        requests_mock.reset_mock()
        requests_mock.register_uri(method, base + path, json=response)

        result = call()

        assert requests_mock.call_count == 1
        request = requests_mock.last_request
        assert request.method == method
        assert urlparse(request.url).path == urlparse(base + path).path
        if body is not _UNSET:
            assert (request.json() if request.body else None) == body
        if qs is not _UNSET:
            assert parse_qs(urlparse(request.url).query) == qs
        assert result == response
        return request

    return check
