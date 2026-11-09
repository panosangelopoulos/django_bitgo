import os

BITGO_API_URL = os.environ.get("BITGO_API_URL", "https://app.bitgo-test.com/")
BITGO_API_VERSION = os.environ.get("BITGO_API_VERSION", "api/v2/")
BITGO_WALLET_ID = os.environ.get("BITGO_WALLET_ID")
BITGO_EXPRESS_URL = os.environ.get("BITGO_EXPRESS_URL", "http://localhost:3080/")
