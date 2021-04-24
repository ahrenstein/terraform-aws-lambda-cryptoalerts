#!/usr/bin/env python3
"""Manage DynamoDB tables to track alert rate limits"""
#
# Python Script:: dynamo_functions.py
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

import datetime
import boto3


def set_last_alert_time(bot_name: str):
    """Set the last time the bot alerted in DynamoDB

    Args:
    bot_name: The bot name stored in the DynamoDB table
    """
    timestamp = str(datetime.datetime.utcnow())
    dynamodb_client = boto3.client('dynamodb')
    try:
        response = dynamodb_client.put_item(TableName="crypto-alerts",
                                            Item={
                                                'BotName': {'S': bot_name},
                                                'LastAlertTime': {'S': timestamp}
                                            })
        print("DEBUGGING: Set last alert results: %s" % response)
    except Exception as err:
        print("Error: Can't put alert time due to %s" % err)


def get_last_alert_time(bot_name: str) -> str:
    """Get the last time the bot alerted from DynamoDB

    Args:
    bot_name: The bot name stored in the DynamoDB table

    Returns:
    last_alert_time: The last alert time
    """
    dynamodb_client = boto3.client('dynamodb')
    try:
        response = dynamodb_client.get_item(TableName="crypto-alerts",
                                            Key={
                                                'BotName': {'S': bot_name}
                                            })
        return response['Item'].get('LastAlertTime').get('S')
    except Exception as err:
        print("Error: Can't get alert time due to %s" % err)
        return "NO_LAST_ALERT_TIME"


def outside_alert_limit(last_alert_time: str, rate_limit_minutes: int) -> bool:
    """Check if the bot is outside the alert limit

    Args:
        last_alert_time: The last alert time
        rate_limit_minutes: The rate limit between alerts

    Returns:
    alert_permitted: A bool that is true if alerts should be permitted
    """
    if last_alert_time == "NO_LAST_ALERT_TIME":
        return True
    current_time = datetime.datetime.utcnow()
    previous_alert_time = datetime.datetime.strptime(last_alert_time, '%Y-%m-%d %H:%M:%S.%f')
    time_delta_in_minutes = round((current_time - previous_alert_time).total_seconds() / 60, 0)
    if time_delta_in_minutes > rate_limit_minutes:
        return True
    return False
