# django_bitgo

Django library for BitGo

[![Downloads](https://static.pepy.tech/personalized-badge/django-bitgo?period=month&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/django-bitgo)

# Overview

Django BitGo is a powerful and flexible library for connecting your BitGo account and integrate it with your Django project.

---

# Requirements

- Python (3.9, 3.10, 3.11, 3.12, 3.13)
- Django (4.2, 5.0, 5.1, 5.2)

We **highly recommend** and only officially support the latest patch release of
each Python and Django series.

# Installation

Install using `pip` ...

    pip install django-bitgo

Install using `poetry` ...

```
poetry add django-bitgo
```

Add `'django_bitgo'` to your `INSTALLED_APPS` setting.

```python
INSTALLED_APPS = [
    ...
    'django_bitgo',
]
```

# Configuration

Set these in your Django settings (or environment):

| Setting | Default | Purpose |
| --- | --- | --- |
| `BITGO_ACCESS_TOKEN` (env var) | - | Access token used for every request |
| `BITGO_API_URL` | `https://app.bitgo-test.com/` | BitGo platform (use `https://app.bitgo.com/` in production) |
| `BITGO_API_VERSION` | `api/v2/` | API prefix |
| `BITGO_EXPRESS_URL` | `http://localhost:3080/` | Your BitGo Express instance (needed to sign/send) |
| `BITGO_WALLET_ID` | - | Default wallet id for wallet-scoped resources |

Every resource accepts an optional `client` (a `BitGoClient`) and, where relevant, a
default `wallet_id`; any method's `wallet_id`/`coin` argument overrides it. Most methods
also take `payload` (extra JSON body fields) or `params` (extra query parameters), so any
field from the [BitGo API reference](https://developers.bitgo.com/reference) can be passed.

## Errors

All failures raise `django_bitgo.exceptions.BitGoException`. For HTTP errors it carries
`status_code`, `error_name` (BitGo's `name` code), `request_id` and `response_body`.

## Pagination

List endpoints return BitGo's `nextBatchPrevId`. `iter_pages` follows it for you:

```python
from django_bitgo.resource import iter_pages

for page in iter_pages(Wallet().list_wallets, coin="tbtc"):
    for wallet in page["wallets"]:
        ...
```

# API Reference

## Wallets

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

## Addresses

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

## Transfers

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

## Webhooks

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

## Wallet policies

```python
from django_bitgo.wallets.policy import Policy

policy = Policy(wallet_id=WALLET_ID)
rule = {"id": "daily-limit", "type": "velocityLimit", "condition": {...}, "action": {"type": "getApproval"}}
policy.create_rule(rule, coin=COIN)
policy.update_rule(rule, coin=COIN)
policy.remove_rule(rule, coin=COIN)
policy.get_rules(coin=COIN)
```

## Wallet sharing

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

## Transaction requests

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

## Pending approvals

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

## Keychains

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

## Enterprises

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

## Users

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

## BitGo Express (signing and sending)

Anything that signs with your user key goes through
[BitGo Express](https://developers.bitgo.com/reference/express-overview), which you run
yourself, e.g. `docker run -p 3080:3080 bitgo/express:latest`.

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

## Not covered

BitGo's platform also exposes product APIs outside wallet custody (Prime trading,
staking, Go Network settlements, fiat/ACH, KYC/KYB, stablecoin minting, organisation
management, Lightning), plus low-level TSS signing-protocol endpoints that BitGo
Express/BitGoJS drive for you. These are not wrapped; you can still call them with
`BitGoClient().request(method=..., path=...)`.
