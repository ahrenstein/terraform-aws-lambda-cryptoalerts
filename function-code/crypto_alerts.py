#!/usr/bin/env python3
"""Check CoinGecko for a cryptocurrency coin/token price and post it to Discord"""
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
import dynamo_functions
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
    bot_name = os.environ.get('BOT_NAME', "")
    dynamodb = os.environ.get('DYNAMO_DB', False)
    alert_rate = int(os.environ.get('ALERT_RATE_LIMIT', 60))
    cryptocurrency = os.environ['CRYPTOCURRENCY']
    alert_price = float(os.environ['ALERT_PRICE'])
    crossing_up = os.environ.get('CROSSING_UP', False)
    coinbase_api_key = os.environ.get('COINBASE_API_KEY', "")
    coinbase_api_secret = os.environ.get('COINBASE_API_SECRET', "")
    blocknative_api_key = os.environ.get("BLOCKNATIVE_API_KEY", "")
    discord_webhook_url = os.environ['DISCORD_WEBHOOK_URL']
    if cryptocurrency == "GASFEES":
        gas_price = gas_fee_check(blocknative_api_key)
        gas_alerting(gas_price, alert_price, discord_webhook_url,
                     dynamodb, bot_name, alert_rate, crossing_up)
    else:
        crypto_alerting(cryptocurrency, alert_price, coinbase_api_key, coinbase_api_secret,
                        discord_webhook_url, dynamodb, bot_name, alert_rate, crossing_up)


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


def gas_fee_check(api_key: str) -> float:
    """Check the price of Ethereum gas fees via Blocknative to see
    if Basefee fell below the minimum "price"

    Args:
        api_key: The Blocknative API key
    Returns:
        basefee: The basefee of gas in gwei
    """
    api_url = 'https://api.blocknative.com/gasprices/blockprices'
    request_headers = {"Authorization": api_key}
    result = requests.get(api_url, headers=request_headers).json()
    for block in result["blockPrices"]:
        basefee = block['baseFeePerGas']
    return float(basefee)


def gas_alerting(gas_price, alert_price, discord_webhook_url, dynamodb,
                 bot_name, alert_rate, crossing_up):
    """Alerting logic for gas prices

        Args:
            gas_price: AWS Lambda event
            alert_price: AWS Lambda context
            discord_webhook_url: The discord_webhook_url
            dynamodb: Use DynamoDB?
            bot_name: The bot's name
            alert_rate: The alert rate
            crossing_up: Are we alerting on crossing up?
    """
    if crossing_up == "false":
        if gas_price <= alert_price:
            print("DEBUGGING:\n Gas Below Maximum %s " % gas_price)
            if dynamodb is False:
                discord_message = "According to **Blocknative** the *basefee**" \
                                  " currently costs **%s**" % gas_price
                post_discord_message(discord_webhook_url, discord_message)
            else:
                # Get the last time the bot alerted
                last_alert = dynamo_functions.get_last_alert_time(bot_name)
                ready_to_alert = dynamo_functions.outside_alert_limit(last_alert, alert_rate)
                if ready_to_alert is True:
                    dynamo_functions.set_last_alert_time(bot_name)
                    discord_message = "According to **Blocknative** the *basefee**" \
                                      " currently costs **%s**" % gas_price
                    post_discord_message(discord_webhook_url, discord_message)
                    dynamo_functions.set_last_alert_time(bot_name)
                else:
                    print("DEBUGGING: Last alert time too recent")
        else:
            print("DEBUGGING:\n Gas Above Maximum %s " % gas_price)
    else:
        if gas_price >= alert_price:
            print("DEBUGGING:\n Gas Above Minimum %s " % gas_price)
            if dynamodb is False:
                discord_message = "According to **Blocknative** the *basefee**" \
                                  " currently costs **%s**" % gas_price
                post_discord_message(discord_webhook_url, discord_message)
            else:
                # Get the last time the bot alerted
                last_alert = dynamo_functions.get_last_alert_time(bot_name)
                ready_to_alert = dynamo_functions.outside_alert_limit(last_alert, alert_rate)
                if ready_to_alert is True:
                    dynamo_functions.set_last_alert_time(bot_name)
                    discord_message = "According to **Blocknative** the *basefee**" \
                                      " currently costs **%s**" % gas_price
                    post_discord_message(discord_webhook_url, discord_message)
                    dynamo_functions.set_last_alert_time(bot_name)
                else:
                    print("DEBUGGING: Last alert time too recent")
        else:
            print("DEBUGGING:\n Gas Below Minimum %s " % gas_price)


def crypto_alerting(cryptocurrency, alert_price, coinbase_api_key, coinbase_api_secret,
                    discord_webhook_url, dynamodb, bot_name, alert_rate, crossing_up):
    """Alerting logic for crypto prices

            Args:
                cryptocurrency: The cryptocurrency to alert on
                alert_price: AWS Lambda context
                coinbase_api_key: The Coinbase API key
                coinbase_api_secret: The Coinbase API secret
                discord_webhook_url: The discord_webhook_url
                dynamodb: Use DynamoDB?
                bot_name: The bot's name
                alert_rate: The alert rate
                crossing_up: Are we alerting on crossing up?
    """
    # Select and execute correct price checker
    if coinbase_api_key == "":
        api_used = "CoinGecko"
        current_price = coingecko_price_check(cryptocurrency)
    else:
        api_used = "Coinbase"
        current_price = coinbase_price_check(coinbase_api_key,
                                             coinbase_api_secret, cryptocurrency)
    # Alerting
    if crossing_up == "false":
        if current_price <= float(alert_price):
            print("DEBUGGING:\nBelow Minimum")
            print("API: %s\ncoin: %s\ncoin_current_price: %s\ntarget_price:"
                  " %s" % (api_used, cryptocurrency, current_price, alert_price))
            if dynamodb is False:
                discord_message = "According to **%s**, **%s** has dropped" \
                                  " below **%s** and is currently at **%s**!" \
                                  % (api_used, cryptocurrency, alert_price, current_price)
                post_discord_message(discord_webhook_url, discord_message)
            else:
                last_alert = dynamo_functions.get_last_alert_time(bot_name)
                ready_to_alert = dynamo_functions.outside_alert_limit(last_alert, alert_rate)
                if ready_to_alert is True:
                    discord_message = "According to **%s**, **%s** has dropped" \
                                      " below **%s** and is currently at **%s**!" \
                                      % (api_used, cryptocurrency, alert_price, current_price)
                    post_discord_message(discord_webhook_url, discord_message)
                    dynamo_functions.set_last_alert_time(bot_name)
                else:
                    print("DEBUGGING: Last alert time too recent")

        else:
            print("DEBUGGING:\nAbove Minimum")
            print("API: %s\ncoin: %s\ncoin_current_price: %s\nminimum_price:"
                  " %s" % (api_used, cryptocurrency, current_price, alert_price))
    else:
        if current_price >= float(alert_price):
            print("DEBUGGING:\nAbove Maximum")
            print("API: %s\ncoin: %s\ncoin_current_price: %s\ntarget_price:"
                  " %s" % (api_used, cryptocurrency, current_price, alert_price))
            if dynamodb is False:
                discord_message = "According to **%s**, **%s** has risen" \
                                  " above **%s** and is currently at **%s**!" \
                                  % (api_used, cryptocurrency, alert_price, current_price)
                post_discord_message(discord_webhook_url, discord_message)
            else:
                last_alert = dynamo_functions.get_last_alert_time(bot_name)
                ready_to_alert = dynamo_functions.outside_alert_limit(last_alert, alert_rate)
                if ready_to_alert is True:
                    discord_message = "According to **%s**, **%s** has risen" \
                                      " above **%s** and is currently at **%s**!" \
                                      % (api_used, cryptocurrency, alert_price, current_price)
                    post_discord_message(discord_webhook_url, discord_message)
                    dynamo_functions.set_last_alert_time(bot_name)
                else:
                    print("DEBUGGING: Last alert time too recent")

        else:
            print("DEBUGGING:\nBelow Maximum")
            print("API: %s\ncoin: %s\ncoin_current_price: %s\ntarget_price:"
                  " %s" % (api_used, cryptocurrency, current_price, alert_price))
