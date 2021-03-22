#!/usr/bin/env python3
"""Check CoinGecko for a cryptocurrency coin/token price and post it to Discord

"""
#
# Python Script:: crypto_alerts.py
#
# Linter:: pylint
# Environment: Lambda
#
# Copyright 2021, Matthew Ahrenstein, All Rights Reserved.
#
# Maintainers:
# - Matthew Ahrenstein: @ahrenstein
#
# See LICENSE
#

import os
import time
import hmac
import hashlib
import requests
from requests.auth import AuthBase
from pycoingecko import CoinGeckoAPI
from discord_webhook import DiscordWebhook


# Create custom authentication for Coinbase API
# as per https://developers.coinbase.com/docs/wallet/api-key-authentication
class CoinbaseWalletAuth(AuthBase):
    """
    Coinbase provided authentication method with minor fixes
    """
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def __call__(self, request):
        timestamp = str(int(time.time()))
        message = timestamp + request.method + request.path_url + (request.body or '')
        # Coinbase's code example is wrong. The key and message must be converted to bytes for HMAC
        key_bytes = bytes(self.secret_key, 'latin-1')
        data_bytes = bytes(message, 'latin-1')
        signature = hmac.new(key_bytes, data_bytes, hashlib.sha256).hexdigest()

        request.headers.update({
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
        })
        return request


def lambda_handler(event, context):
    """The standard AWS lambda_handler

    Args:
        event: AWS Lambda event
        context: AWS Lambda context
    """
    print("Running Cryptocurrency price check")
    # Print AWS Lambda event and context to clean up linting
    print("AWS Event: %s\n"
          "AWS Context: %s" %(event, context))
    # Importing environment variables from AWS Lambda
    cryptocurrency = os.environ['CRYPTOCURRENCY']
    alert_price = os.environ['ALERT_PRICE']
    coinbase_api_key = os.environ.get('COINBASE_API_KEY', "")
    coinbase_api_secret = os.environ.get('COINBASE_API_SECRET', "")
    discord_webhook_url = os.environ['DISCORD_WEBHOOK_URL']
    # Instantiate variables to use for alerting logic
    current_price = None
    api_used = None
    if cryptocurrency == "GASFEES":
        gas_price = gas_fee_check()
        if gas_price <= alert_price:
            print("DEBUGGING:\n Gas Below Maximum")
            discord_message = "Accordng to **GAS NOW** a **fast** transaction" \
                              " currently costs **%s**" % gas_price
            post_discord_message(discord_webhook_url, discord_message)
        else:
            print("DEBUGGING:\n Gas Above Maximum")
    else:
        # Select and execute correct price checker
        if coinbase_api_key == "":
            api_used = "CoinGecko"
            current_price = coingecko_price_check(cryptocurrency)
        else:
            api_used = "Coinbase"
            current_price = coinbase_price_check(coinbase_api_key,
                                                 coinbase_api_secret, cryptocurrency)
        # Alerting
        if current_price < float(alert_price):
            discord_message = "According to **%s**, **%s** has dropped" \
                              " below **%s** and is currently at **%s**!"\
                              % (api_used, cryptocurrency, alert_price, current_price)
            post_discord_message(discord_webhook_url, discord_message)
            print("DEBUGGING:\nBelow Minimum")
            print("API: %s\ncoin: %s\ncoin_current_price: %s\nminimum_price:"
                  " %s" % (api_used, cryptocurrency, current_price, alert_price))
        else:
            print("DEBUGGING:\nAbove Minimum")
            print("API: %s\ncoin: %s\ncoin_current_price: %s\nminimum_price:"
                  " %s" % (api_used, cryptocurrency, current_price, alert_price))


def post_discord_message(discord_webhook_url, discord_message):
    """Post a message to Discord.

    Args:
        discord_webhook_url: A Discord Webhook URL
        discord_message: The message to send
    """
    webhook = DiscordWebhook(url=discord_webhook_url, content=discord_message)
    _ = webhook.execute()


def coinbase_price_check(coinbase_api_key, coinbase_api_secret,
                         coin):
    """Check the price of a cryptocurrency against Coinbase to see
    if it fell below the minimum price

    Args:
        coinbase_api_key: An API key for Coinbase APIv2
        coinbase_api_secret: An API secret for Coinbase APIv2
        coin: The coin/token that we care about

    Returns:
        coin_current_price: The current price of the coin
    """
    # Instantiate Coinbase API and query the price
    api_url = 'https://api.coinbase.com/v2/'
    coinbase_auth = CoinbaseWalletAuth(coinbase_api_key, coinbase_api_secret)
    api_query = "prices/%s-USD/sell" % coin
    result = requests.get(api_url + api_query, auth=coinbase_auth)
    coin_current_price = float(result.json()['data']['amount'])
    return coin_current_price


def coingecko_price_check(coin):
    """Check the price of a cryptocurrency against CoinGecko to see
    if it fell below the minimum price

    Args:
        coin: The coin/token that we care about

    Returns:
        coin_current_price: The current price of the coin
    """
    # Instantiate CoinGecko API and process query
    coingecko_client = CoinGeckoAPI()
    coin_current_price = float(coingecko_client.get_price
                               (ids=coin, vs_currencies="usd")[coin]['usd'])
    return coin_current_price


def gas_fee_check():
    """Check the price of Ethereum gas fees via GAS NOW to see
    if fast fell below the minimum "price"

    Returns:
        fast_gwei: The fast price of gas in gwei
    """
    api_url = 'https://www.gasnow.org/api/v3/gas/price'
    result = requests.get(api_url)
    fast_gwei = int(result.json()['data']['fast'] *.000000001)
    return fast_gwei
