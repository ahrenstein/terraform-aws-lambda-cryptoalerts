Terraform Module - AWS Cryptocurrency Alerts Lambda: Testing
============================================================
I test my Terraform modules in AWS before changes are merged.

Testing Requirements
--------------------
All modules tested must follow these testing rules:

1. All modules must be tested against an AWS account with all optional variables tested.
2. Changes to modules should be tested to avoid breaking existing infrastructure.
3. Code should pass `pre-commit` checks.

pre-commit
----------
This repo uses Yelp's [pre-commit](https://pre-commit.com/) to manage some pre-commit hooks automatically.  
In order to use the hooks, make sure you have `pre-commit`, `terraform`, and `pylint` in your `$PATH`.  
Once in your path you should run `pre-commit install` in order to configure it. If you push commits that fail pre-commit, your PR will
not be merged.

Return to [README](README.md)
