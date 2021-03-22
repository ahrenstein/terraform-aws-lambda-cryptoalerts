#
# Project:: Terraform Module - lambda-cryptoalerts
#
# Copyright 2021, Matthew Ahrenstein, All Rights Reserved.
#
# Maintainers:
# - Matthew Ahrenstein: @ahrenstein
#
# See LICENSE
#
locals {
  base_tags = {
    "Module" = "true"
  }
  tags = merge(local.base_tags, var.tags)
}

variable "cryptocurrency" {
  type        = string
  description = "REQUIRED: The name of a cryptocurrency that CoinGecko tracks"
}

variable "minimum_value" {
  type        = number
  description = "REQUIRED: The minimum acceptable price in USD you wish to alert on"
}

variable "coinbase_api_key" {
  type        = string
  description = "OPTIONAL: The Coinbase API key if you prefer to use Coinbase over CoinGecko"
  default     = ""
}

variable "coinbase_api_secret" {
  type        = string
  description = "OPTIONAL: The Coinbase API secret if you prefer to use Coinbase over CoinGecko"
  default     = ""
}

variable "discord_webhook_url" {
  type        = string
  description = "REQUIRED: The Discord server webhook URL you will post messages to"
}

variable "rate" {
  type        = number
  description = "OPTIONAL: Set the rate in minutes that the cron runs for"
  default     = 5
}

variable "tags" {
  type        = map(string)
  description = "OPTIONAL: You should have a group of tags such as \"CostTracking\""
  default     = {}
}

variable "name_postfix" {
  type        = string
  default     = "-alert"
  description = "OPTIONAL: Change the postfix of the Lambda function name"
}
