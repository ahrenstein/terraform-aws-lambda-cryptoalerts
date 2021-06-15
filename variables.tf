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

variable "target_price" {
  type        = number
  description = "REQUIRED: The target price in USD you wish to alert on"
}

variable "crossing_up" {
  type        = bool
  description = "OPTIONAL: Check if the current price is above the target instead of below"
  default     = false
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

variable "dynamodb" {
  type        = bool
  description = "OPTIONAL: Enable using DynamoDB to track last alert time in"
  default     = false
}

variable "alert_rate_limit" {
  type        = number
  description = "OPTIONAL: The rate in minutes that alerts may repeat"
  default     = 60
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

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
