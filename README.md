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
  minimum_value           = 46000.00
  rate                    = 30 // Optional: The run interval in minutes (default: 5)
  coinbase_api_key        = "XXXXX" // Optional: If you don't specify this then CoinGecko will be used 
  coinbase_api_secret     = "YYYYY" // Optional: If you don't specify this then CoinGecko will be used
  discord_webhook_url     = "https://discord.com/api/webhooks/XXXXX/YYYYYYYY" // The Discord webhook that will post the alerts
  tags = { // These values are optional
    SomeTag = "SomeValue"
  }
}
```

Testing
-------
This module is fully tested in AWS in a live environment.  
[TESTING.md](TESTING.md) contains details and instructions for testing. 

Donations
---------
I have GitHub sponsors enabled but for crypto related projects, I'm also happy to accept [Bitcoin](images/bitcoin.png), and [Ethereum](images/ethereum.png)
