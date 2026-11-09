from django_bitgo.resource import Resource, compact, require


class User(Resource):
    def me(self):
        """GET /user/me - the user owning the access token."""
        return self.get_user("me")

    def get_user(self, user_id: str, params: dict = None):
        """GET /user/{id}"""
        require(user_id, "User id")
        return self._get(f"user/{user_id}", params=params)

    def get_session(self):
        """GET /user/session"""
        return self._get("user/session")

    def unlock(self, otp: str, duration: int = None):
        """POST /user/unlock - unlocks the session for sensitive operations (e.g. spends)."""
        require(otp, "OTP")
        return self._post("user/unlock", payload=compact(otp=otp, duration=duration))

    def lock(self):
        """POST /user/lock"""
        return self._post("user/lock")

    def logout(self):
        """GET /user/logout"""
        return self._get("user/logout")

    def get_sharing_key(self, email: str):
        """POST /user/sharingkey - public key used to share a wallet with ``email``."""
        require(email, "Email")
        return self._post("user/sharingkey", payload={"email": email})

    # --- Access tokens ----------------------------------------------------

    def list_access_tokens(self, params: dict = None):
        """GET /user/accesstoken"""
        return self._get("user/accesstoken", params=params)

    def add_access_token(self, label: str, otp: str, payload: dict = None):
        """POST /user/accesstoken - ``payload`` holds ``scope``, ``duration``,
        ``ipRestrict``, ``spendingLimits``, ``enterprise``, ..."""
        require(label, "Label")
        require(otp, "OTP")
        return self._post(
            "user/accesstoken",
            payload={**(payload or {}), "label": label, "otp": otp},
        )

    def delete_access_token(self, token_id: str):
        """DELETE /user/accesstoken/{token}"""
        require(token_id, "Access token id")
        return self._delete(f"user/accesstoken/{token_id}")
