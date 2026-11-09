import pytest

from django_bitgo.exceptions import BitGoException
from django_bitgo.user import User


@pytest.mark.parametrize(
    "call, method, path, body",
    [
        (lambda u: u.me(), "GET", "user/me", None),
        (lambda u: u.get_user("u1"), "GET", "user/u1", None),
        (lambda u: u.get_session(), "GET", "user/session", None),
        (
            lambda u: u.unlock("000000", duration=600),
            "POST",
            "user/unlock",
            {"otp": "000000", "duration": 600},
        ),
        (lambda u: u.lock(), "POST", "user/lock", None),
        (lambda u: u.logout(), "GET", "user/logout", None),
        (
            lambda u: u.get_sharing_key("a@b.c"),
            "POST",
            "user/sharingkey",
            {"email": "a@b.c"},
        ),
        (lambda u: u.list_access_tokens(), "GET", "user/accesstoken", None),
        (
            lambda u: u.add_access_token(
                "ci", "000000", payload={"scope": ["wallet_view_all"]}
            ),
            "POST",
            "user/accesstoken",
            {"label": "ci", "otp": "000000", "scope": ["wallet_view_all"]},
        ),
        (
            lambda u: u.delete_access_token("t1"),
            "DELETE",
            "user/accesstoken/t1",
            None,
        ),
    ],
)
def test_user_endpoints(client, check_call, call, method, path, body):
    check_call(lambda: call(User(client=client)), method, path, body=body)


@pytest.mark.parametrize(
    "call",
    [
        lambda u: u.get_user(""),
        lambda u: u.unlock(""),
        lambda u: u.add_access_token("ci", ""),
        lambda u: u.delete_access_token(""),
    ],
)
def test_user_validation(client, call):
    with pytest.raises(BitGoException):
        call(User(client=client))
