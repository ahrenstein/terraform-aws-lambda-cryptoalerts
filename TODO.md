Terraform Module - AWS Cryptocurrency Alerts Lambda: To Dos
===========================================================
A list of all the things that really should be done at some point and PRs that resolve them are very welcome.

Version 2.0.0
-------------

1. Move `discord_webhook_url`, `coinbase_api_key`, and `coinbase_api_secret` to AWS Secrets. This would make deploys more manual, but they are credentials
and should be protected better.
2. Slack Webhook support (maybe if demand for it exists)

Return to [README](README.md)
