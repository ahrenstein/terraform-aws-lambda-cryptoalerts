Terraform Module - AWS Cryptocurrency Alerts Lambda
===================================================
This repo contains the Terraform module for an AWS Lambda function that runs on a schedule and checks the value of a cryptocurrency
against CoinGecko (default) or Coinbase. Currently, it supports Discord for alerts.

Infrastructure Created
----------------------
The following infrastructure is created using this module:

1. An AWS Lambda function that runs using a CloudWatch cron schedule

Requirements
------------
You will need the following on your computer:

1. Terraform 0.14+ (Untested on lower versions)
2. pip3 installed at `/user/local/bin/pip3`

Variables
---------
The following variables are required.

```hcl
module "cryptocurrency-alert" {
  source                  = "git::https://github.com/ahrenstein/terraform-aws-lambda-cryptoalerts"
  cryptocurrency          = "BTC"
  target_price            = 46000.00
  crossing_up             = true //Optional: Alert if coin is above current price (default: false)
  rate                    = 10 // Optional: The run interval in minutes (default: 5)
  name_postfix            = "-under-46k" // Optional: Override the Lambda postfix name
  coinbase_api_key        = "XXXXX" // Optional: If you don't specify this then CoinGecko will be used 
  coinbase_api_secret     = "YYYYY" // Optional: If you don't specify this then CoinGecko will be used
  blocknative_apy_key     = "ZZZZZ" // Optional: If you are getting the gas fee rates, you must provide this
  dynamodb                = true // Optional: Use DynamoDB to enable alert rate liming (default: false)
  alert_rate_limit        = 30 // Optional: Rate limit in minutes before an alert can trigger again since the last one (default: 60)
  discord_webhook_url     = "https://discord.com/api/webhooks/XXXXX/YYYYYYYY" // The Discord webhook that will post the alerts
  tags = { // These values are optional
    SomeTag = "SomeValue"
  }
}
```

Rate Limiting Alerts
--------------------
If you specify enabling DynamoDB to store the last alert timestamp, you can limit how frequently an alert triggers
in order to avoid excess noise during an extended dip period.  
**The DynamoDB must be created outside this module and must be named `crypto-alerts`**  
If DynamoDB is enabled you can also specify the rate limit in minutes.

Example Terraform code for an appropriate Dynamo-DB table:

```hcl
resource "aws_dynamodb_table" "crypto-alerts" {
  name           = "crypto-alerts"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "BotName"

  attribute {
    name = "BotName"
    type = "S"
  }

  tags = {
    Name         = "crypto-alerts"
  }
}
```

Gas Alerts
----------
If you set the cryptocurrency value to `GASFEES` instead of checking a cryptocurrency value,
you will get alerts if the fast price of gas **on Ethereum Mainnet** is below the `minimum_value` according to [GAS NOW](https://www.gasnow.org/).  
GAS NOW does not care for frequent pulls, so it's recommended to keep that to a rate of 10+ minutes.

Testing
-------
This module is fully tested in AWS in a live environment.  
[TESTING.md](TESTING.md) contains details and instructions for testing. 

Donations
---------
Any and all donations are greatly appreciated.  
I have GitHub Sponsors configured however I happily prefer cryptocurrency:

ETH/ERC20s: ahrenstein.eth (0x288f3d3df1c719176f0f6e5549c2a3928d27d1c1)  
BTC: 3HrVPPwTmPG8LKBt84jbQrVjeqDbM1KyEb
