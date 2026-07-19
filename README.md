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

# API Reference

## The `wallets` module

The top-level module for wallets.

Refer to the [BitGo API documentation](https://developers.bitgo.com/) for details on the underlying endpoints.

### Wallet

```python
from django_bitgo.wallets.wallet import Wallet

wallet = Wallet()
wallet.list_wallets(coin=COIN)
wallet.get_wallet(wallet_id=WALLET_ID, coin=COIN)

# `payload` must already contain pre-generated keys (`keys`, `m`, `n`, ...) -
# this library does not generate or custody keys for you.
wallet.create_wallet(coin=COIN, payload=payload)
```

### Address

```python
from django_bitgo.wallets.address import Address

address = Address(wallet_id=WALLET_ID)
address.get_address(address_id=ADDRESS_ID, coin=COIN)
address.list_addresses(coin=COIN)
address.create_address(coin=COIN, payload=payload)
address.deploy_address(address_id=ADDRESS_ID, coin=COIN)
```

### Transfer

```python
from django_bitgo.wallets.transfer import Transfer

transfer = Transfer(wallet_id=WALLET_ID)
transfer.list_transfers(coin=COIN)
transfer.get_transfer(transfer_id=TRANSFER_ID, coin=COIN)
```
