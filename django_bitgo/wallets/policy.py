from django_bitgo.resource import Resource, require


class Policy(Resource):
    """Wallet policy rules (whitelists, velocity limits, ...).

    A rule payload looks like::

        {
            "id": "my-velocity-limit",
            "type": "velocityLimit",
            "condition": {"amountString": "1000000", "timeWindow": 86400, ...},
            "action": {"type": "getApproval"},
        }
    """

    def _rule_path(self, coin: str, wallet_id: str) -> str:
        return f"{coin}/wallet/{self._wallet_id(wallet_id)}/policy/rule"

    def create_rule(self, rule: dict, coin: str = "tbtc", wallet_id: str = ""):
        """POST /{coin}/wallet/{walletId}/policy/rule"""
        self._validate(rule)
        return self._post(self._rule_path(coin, wallet_id), payload=rule)

    def update_rule(self, rule: dict, coin: str = "tbtc", wallet_id: str = ""):
        """PUT /{coin}/wallet/{walletId}/policy/rule"""
        self._validate(rule)
        return self._put(self._rule_path(coin, wallet_id), payload=rule)

    def remove_rule(self, rule: dict, coin: str = "tbtc", wallet_id: str = ""):
        """DELETE /{coin}/wallet/{walletId}/policy/rule"""
        self._validate(rule)
        return self._delete(self._rule_path(coin, wallet_id), payload=rule)

    def get_rules(self, coin: str = "tbtc", wallet_id: str = ""):
        """Returns the wallet's current policy rules (from GET /{coin}/wallet/{walletId})."""
        wallet = self._get(f"{coin}/wallet/{self._wallet_id(wallet_id)}")
        return (wallet.get("admin") or {}).get("policy", {}).get("rules", [])

    @staticmethod
    def _validate(rule: dict):
        require(rule, "Policy rule")
        require(rule.get("id"), "Policy rule id")
