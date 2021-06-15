Terraform Module - AWS Cryptocurrency Alerts Lambda: Changelog
==============================================================
A list of all the changes made to this repo, and the Terraform module it contains

Version 1.3.0
-------------

1. Alert price is a float now, so low cap coins can be monitored
2. **BREAKING CHANGE**: `minimum_value` is now `target_price`
2. Optionally alert if the current price is higher than the target price instead of below

Version 1.2.0
-------------

1. Support for rate limiting alerts via a DynamoDB table (created separately)

Version 1.1.0
-------------

1. Support for Ethereum Mainnet gas fees alerting
2. Removed redundant comments
3. Added an optional `name_postfix` variable to the lambda function and role names

Version 1.0.0
-------------

1. initial Release of repository.

Return to [README](README.md)
