# django-bitgo

A Django library for the [BitGo](https://www.bitgo.com/) Platform API: wallets,
addresses, transfers, webhooks, policies and approvals, plus sending funds through
BitGo Express.

[![CI](https://github.com/panosangelopoulos/django_bitgo/actions/workflows/ci.yml/badge.svg)](https://github.com/panosangelopoulos/django_bitgo/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/django-bitgo)](https://pypi.org/project/django-bitgo/)
[![Python versions](https://img.shields.io/pypi/pyversions/django-bitgo)](https://pypi.org/project/django-bitgo/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Downloads](https://static.pepy.tech/personalized-badge/django-bitgo?period=month&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/django-bitgo)

- **Thin and predictable.** Every method maps to one BitGo endpoint and returns the
  decoded JSON response.
- **Covers wallet custody on `/api/v2`.** Wallets, addresses, transfers, webhooks,
  policies, sharing, transaction requests, pending approvals, keychains, enterprises
  and users.
- **Signing through BitGo Express.** Sending, wallet generation, acceleration and
  consolidation go through your own [BitGo Express](#bitgo-express) instance.
  This library never generates, stores or sees private keys.
- **Not limited to wrapped fields.** Pass any extra body field with `payload` or query
  parameter with `params`.

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quickstart](#quickstart)
- [BitGo Express](#bitgo-express)
- [Receiving webhooks in Django](#receiving-webhooks-in-django)
- [Errors](#errors)
- [Pagination](#pagination)
- [API reference](#api-reference)
- [Endpoints not wrapped](#endpoints-not-wrapped)
- [Development](#development)
- [License](#license)

## Requirements

- Python 3.9, 3.10, 3.11, 3.12, 3.13
- Django 4.2, 5.0, 5.1, 5.2

Only the latest patch release of each Python and Django series is officially supported.

## Installation

```bash
pip install django-bitgo
# or
poetry add django-bitgo
```

Add the app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_bitgo",
]
```

## Configuration

Create an access token in the BitGo web app (under *Developer Options* in your settings) and
expose it as the `BITGO_ACCESS_TOKEN` environment variable:

```bash
export BITGO_ACCESS_TOKEN="v2x..."
```

Then set any of these in your Django settings. All are optional:

```python
# settings.py
BITGO_API_URL = "https://app.bitgo-test.com/"  # production: "https://app.bitgo.com/"
BITGO_EXPRESS_URL = "http://localhost:3080/"
BITGO_WALLET_ID = "your-default-wallet-id"
```

| Setting | Default | Purpose |
| --- | --- | --- |
| `BITGO_API_URL` | `https://app.bitgo-test.com/` | BitGo platform URL. The default is the **test** environment. |
| `BITGO_API_VERSION` | `api/v2/` | API path prefix |
| `BITGO_EXPRESS_URL` | `http://localhost:3080/` | Your BitGo Express instance, needed to sign and send |
| `BITGO_WALLET_ID` | none | Default wallet for wallet-scoped resources |

To use a different token per call (for example, per tenant), pass a client explicitly:

```python
from django_bitgo.client import BitGoClient
from django_bitgo.wallets.wallet import Wallet

wallet = Wallet(client=BitGoClient(access_token=token), wallet_id=wallet_id)
```

Every resource takes an optional `client` and a default `wallet_id`. The `wallet_id`
and `coin` arguments on individual methods override them. Coins use BitGo's tickers
(`btc`, `eth`, `sol`, ...); on the test environment they are prefixed with `t`
(`tbtc`, `teth`, ...). Most methods default to `tbtc`.

## Quickstart

```python
from django_bitgo.wallets.address import Address
from django_bitgo.wallets.transfer import Transfer
from django_bitgo.wallets.wallet import Wallet

# List wallets and read a balance
wallets = Wallet().list_wallets(coin="tbtc")
wallet = Wallet().get_wallet(wallet_id=WALLET_ID, coin="tbtc")
print(wallet["label"], wallet["balanceString"])

# Create a deposit address for a customer
address = Address(wallet_id=WALLET_ID).create_address(
    coin="tbtc", payload={"label": "customer-42"}
)
print(address["address"])

# Read incoming transfers
transfers = Transfer(wallet_id=WALLET_ID).list_transfers(
    coin="tbtc", params={"type": "receive", "state": "confirmed"}
)
```

> Use the `...String` balance fields (`balanceString`, `spendableBalanceString`) rather
> than the integer ones. Amounts are in base units (satoshi, wei, ...) and can exceed
> what an integer field holds.

## BitGo Express

BitGo wallets are multi-signature: a send needs your user key plus BitGo's key. BitGo
Express is a small server you run yourself. It decrypts the user key locally with the
wallet passphrase, signs, and forwards the transaction to BitGo. Everything that signs
goes through it.

Run it next to your app:

```bash
docker run -it -p 3080:3080 bitgo/express:latest
# production: add --env prod and TLS (--keypath / --crtpath)
```

Then send funds:

```python
import os

from django_bitgo.express import Express

express = Express(wallet_id=WALLET_ID)
result = express.send_coins(
    address="tb1q...",
    amount="10000",  # base units; strings avoid precision issues
    wallet_passphrase=os.environ["BITGO_WALLET_PASSPHRASE"],
    coin="tbtc",
)
```

If a wallet policy requires approval, the response has a `pendingApproval` instead of a
`txid`. Handle it with [`PendingApproval`](#pending-approvals).

**Security:** never expose Express to the internet, and keep wallet passphrases in a
secret store, not in settings files or source control.

## Receiving webhooks in Django

Register a webhook on a wallet:

```python
from django_bitgo.wallets.webhook import Webhook

Webhook(wallet_id=WALLET_ID).add_wallet_webhook(
    "transfer", "https://example.com/bitgo/webhook/", coin="tbtc",
    payload={"numConfirmations": 1},
)
```

Then handle it with a view. Treat the notification only as a signal: re-fetch the
transfer from BitGo rather than trusting the request body.

```python
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django_bitgo.exceptions import BitGoException
from django_bitgo.wallets.transfer import Transfer


@csrf_exempt
@require_POST
def bitgo_webhook(request):
    event = json.loads(request.body)
    if event.get("type") != "transfer":
        return HttpResponse(status=204)

    try:
        transfer = Transfer(wallet_id=event["wallet"]).get_transfer(
            transfer_id=event["transfer"], coin=event["coin"]
        )
    except BitGoException:
        return HttpResponse(status=502)  # BitGo retries failed deliveries

    if transfer["state"] == "confirmed":
        ...  # credit the customer, idempotently keyed on transfer["id"]

    return HttpResponse(status=200)
```

To check signatures, create a secret with `Webhook().create_webhook_secret(...)`,
then verify each notification with `Webhook().verify_notification(webhook_id,
raw_body, signature)`.

## Errors

Every failure raises `django_bitgo.exceptions.BitGoException`. For HTTP errors it
includes BitGo's error details:

```python
from django_bitgo.exceptions import BitGoException

try:
    Wallet().get_wallet(wallet_id="missing", coin="tbtc")
except BitGoException as exc:
    exc.status_code    # 404
    exc.error_name     # BitGo's error code, e.g. "WalletNotFound"
    exc.request_id     # quote this to BitGo support
    exc.response_body  # the full decoded error body
```

Missing required arguments (such as an empty `wallet_id`) also raise `BitGoException`,
before any request is sent.

## Pagination

List endpoints return up to `limit` results (default 25, maximum 500) and a
`nextBatchPrevId` cursor. `iter_pages` follows the cursor for you:

```python
from django_bitgo.resource import iter_pages

for page in iter_pages(Wallet().list_wallets, coin="tbtc", limit=100):
    for wallet in page["wallets"]:
        ...
```

## API reference

Each method's docstring names the BitGo endpoint it calls. See the
[BitGo API reference](https://developers.bitgo.com/reference) for the full request
and response fields.

### Wallets

```python
from django_bitgo.wallets.wallet import Wallet

wallet = Wallet(wallet_id=WALLET_ID)
wallet.list_wallets(coin=COIN)              # GET /{coin}/wallet
wallet.list_all_wallets()                   # GET /wallets
wallet.count_wallets()
wallet.get_wallet(coin=COIN)
wallet.get_wallet_by_id()                   # no coin needed
wallet.get_wallet_by_address(address=ADDRESS, coin=COIN)
wallet.update_wallet({"label": "Treasury"}, coin=COIN)
wallet.remove_wallet(coin=COIN)
wallet.remove_user(user_id=USER_ID, coin=COIN)
wallet.freeze_wallet(duration=3600, coin=COIN)
wallet.get_total_balances()                 # all coins, or coin=COIN
wallet.get_maximum_spendable(coin=COIN)
wallet.list_unspents(coin=COIN)
wallet.build_transaction({"recipients": [...]}, coin=COIN)
wallet.send_transaction({"halfSigned": {...}}, coin=COIN)
wallet.initiate_transaction({...}, coin=COIN)   # custodial wallets
wallet.change_fee(txid=TXID, coin=COIN)
wallet.build_consolidate_unspents(coin=COIN)
wallet.build_consolidate_account(coin=COIN)

# `payload` must already contain pre-generated keys (`keys`, `m`, `n`, ...) -
# this library does not generate or custody keys for you (see Express.generate_wallet).
wallet.create_wallet(coin=COIN, payload=payload)
```

### Addresses

```python
from django_bitgo.wallets.address import Address

address = Address(wallet_id=WALLET_ID)
address.list_addresses(coin=COIN)
address.get_address(address_id=ADDRESS_ID, coin=COIN)
address.create_address(coin=COIN, payload=payload)
address.update_address(ADDRESS_ID, {"label": "Deposit #1"}, coin=COIN)
address.list_address_balances(coin=COIN)
address.deploy_address(address_id=ADDRESS_ID, coin=COIN)
address.forward_token(ADDRESS_ID, token_name="terc", coin="teth")
```

### Transfers

```python
from django_bitgo.wallets.transfer import Transfer

transfer = Transfer(wallet_id=WALLET_ID)
transfer.list_transfers(coin=COIN, params={"state": "confirmed"})
transfer.get_transfer(transfer_id=TRANSFER_ID, coin=COIN)
transfer.get_transfer_by_sequence_id(SEQUENCE_ID, coin=COIN)
transfer.comment_transfer(TRANSFER_ID, "Invoice 42", coin=COIN)
transfer.list_enterprise_transfers(ENTERPRISE_ID)
transfer.get_fee_estimate(coin=COIN, num_blocks=2)
transfer.get_transaction(TXID, coin=COIN)
```

### Webhooks

```python
from django_bitgo.wallets.webhook import Webhook

webhook = Webhook(wallet_id=WALLET_ID)
webhook.list_wallet_webhooks(coin=COIN)
webhook.add_wallet_webhook("transfer", "https://example.com/hook", coin=COIN)
webhook.remove_wallet_webhook(type="transfer", url="https://example.com/hook", coin=COIN)
webhook.simulate_wallet_webhook(WEBHOOK_ID, coin=COIN, payload={"transferId": TRANSFER_ID})
webhook.list_webhook_notifications(coin=COIN)
webhook.list_block_webhooks(coin=COIN)
webhook.add_block_webhook("https://example.com/blocks", coin=COIN)
webhook.remove_block_webhook("https://example.com/blocks", coin=COIN)
webhook.simulate_block_webhook(WEBHOOK_ID, coin=COIN)
webhook.create_webhook_secret(enterprise_id=ENTERPRISE_ID)
webhook.verify_notification(WEBHOOK_ID, raw_body, signature_header)
```

### Wallet policies

```python
from django_bitgo.wallets.policy import Policy

policy = Policy(wallet_id=WALLET_ID)
rule = {"id": "daily-limit", "type": "velocityLimit", "condition": {...}, "action": {"type": "getApproval"}}
policy.create_rule(rule, coin=COIN)
policy.update_rule(rule, coin=COIN)
policy.remove_rule(rule, coin=COIN)
policy.get_rules(coin=COIN)
```

### Wallet sharing

```python
from django_bitgo.wallets.share import WalletShare

share = WalletShare(wallet_id=WALLET_ID)
share.list_shares()
share.count_shares("active")
share.get_share(SHARE_ID, coin=COIN)
share.create_share(USER_ID, "view", coin=COIN)
share.accept_share(SHARE_ID, coin=COIN)      # view-only; spend shares: Express.accept_share
share.reject_share(SHARE_ID, coin=COIN)
share.cancel_share(SHARE_ID, coin=COIN)
share.resend_share_email(SHARE_ID, coin=COIN)
```

### Transaction requests

```python
from django_bitgo.wallets.tx_request import TxRequest

tx_request = TxRequest(wallet_id=WALLET_ID)
tx_request.create_tx_request({"intentType": "payment", "recipients": [...]})
tx_request.list_tx_requests(params={"states": "pendingApproval"})
tx_request.get_tx_request(TX_REQUEST_ID)
tx_request.cancel_tx_request(TX_REQUEST_ID, reason="duplicate")
tx_request.list_awaiting_signature()
tx_request.list_enterprise_tx_requests(ENTERPRISE_ID)
```

### Pending approvals

```python
from django_bitgo.pending_approval import PendingApproval

approvals = PendingApproval()
approvals.list_pending_approvals(wallet_id=WALLET_ID, state="pending")
approvals.count_pending_approvals()
approvals.get_pending_approval(APPROVAL_ID)
approvals.get_pending_approval_transfer(APPROVAL_ID)
approvals.approve(APPROVAL_ID, otp="000000")
approvals.reject(APPROVAL_ID, memo="Not expected")
approvals.bulk_update([{"id": APPROVAL_ID, "state": "approved"}])
```

### Keychains

```python
from django_bitgo.keychain import Keychain

keychain = Keychain()
keychain.list_keys(coin=COIN)
keychain.get_key(KEY_ID, coin=COIN)
keychain.list_wallet_keys([WALLET_ID])
keychain.add_key({"pub": "xpub..."}, coin=COIN)
keychain.create_bitgo_key(coin=COIN, enterprise=ENTERPRISE_ID)
keychain.create_backup_key(coin=COIN)
keychain.get_tss_pubkey(coin="tsol")
```

### Enterprises

```python
from django_bitgo.enterprise import Enterprise

enterprise = Enterprise()
enterprise.list_enterprises()
enterprise.get_enterprise(ENTERPRISE_ID)
enterprise.update_enterprise(ENTERPRISE_ID, {...})
enterprise.get_fee_address_balance(ENTERPRISE_ID, coin="teth")
enterprise.get_wallet_limits(ENTERPRISE_ID)
enterprise.list_available_assets(ENTERPRISE_ID)
enterprise.add_user(ENTERPRISE_ID, "user@example.com", permission="admin")
enterprise.update_user(ENTERPRISE_ID, {...})
enterprise.remove_user(ENTERPRISE_ID, "user@example.com")
enterprise.list_webhooks(ENTERPRISE_ID)
enterprise.add_webhook(ENTERPRISE_ID, {...})
enterprise.remove_webhook(ENTERPRISE_ID, WEBHOOK_ID)
enterprise.simulate_webhook(ENTERPRISE_ID, WEBHOOK_ID)
```

### Users

```python
from django_bitgo.user import User

user = User()
user.me()
user.get_user(USER_ID)
user.get_session()
user.unlock(otp="000000")          # required before some sensitive operations
user.lock()
user.logout()
user.get_sharing_key("user@example.com")
user.list_access_tokens()
user.add_access_token("ci", otp="000000", payload={"scope": [...]})
user.delete_access_token(TOKEN_ID)
```

### BitGo Express

```python
from django_bitgo.express import Express

express = Express(wallet_id=WALLET_ID)
express.ping()
express.generate_wallet(label="Treasury", enterprise=ENTERPRISE_ID, passphrase=PASSPHRASE, coin=COIN)
express.send_coins(address=ADDRESS, amount="10000", wallet_passphrase=PASSPHRASE, coin=COIN)
express.send_many([{"address": ADDRESS, "amount": "10000"}], wallet_passphrase=PASSPHRASE, coin=COIN)
express.sign_transaction({"txPrebuild": {...}, "walletPassphrase": PASSPHRASE}, coin=COIN)
express.sign_tss_transaction({...}, coin="tsol")
express.accelerate_transaction(PASSPHRASE, cpfp_tx_ids=[TXID], coin=COIN)
express.consolidate_unspents(PASSPHRASE, coin=COIN)
express.fanout_unspents(PASSPHRASE, coin=COIN)
express.consolidate_account(PASSPHRASE, coin="teth")
express.sweep(ADDRESS, PASSPHRASE, coin=COIN)
express.share_wallet("user@example.com", "view,spend", wallet_passphrase=PASSPHRASE, coin=COIN)
express.accept_share(SHARE_ID, user_password=PASSWORD, coin=COIN)
express.verify_address(ADDRESS, coin=COIN)
express.canonical_address(ADDRESS, coin="tbch")
express.is_wallet_address(ADDRESS, keychains=[...], coin="teth")
```

## Endpoints not wrapped

BitGo also offers products outside wallet custody: Prime trading, staking, Go Network
settlements, fiat/ACH, KYC/KYB, stablecoin minting, organisation management and
Lightning. These are not wrapped, and neither are the low-level TSS signing-protocol
endpoints that Express drives for you. You can call any of them with the client
directly:

```python
from django_bitgo.client import BitGoClient

response = BitGoClient().request(method="GET", path="tbtc/wallet/WALLET_ID/sequenceIds")
response.json()
```

## Development

```bash
poetry install
poetry run pytest
poetry run black .
```

CI runs the test suite and `black --check` across every supported Python and Django
combination.

## License

[MIT](LICENSE)
