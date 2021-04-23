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

# Download Lambda dependencies from requirements.txt
resource "null_resource" "pip" {
  triggers = {
    main         = base64sha256(file("${path.module}/function-code/crypto_alerts.py"))
    requirements = base64sha256(file("${path.module}/function-code/requirements.txt"))
  }

  provisioner "local-exec" {
    command = "/usr/local/bin/pip3 install -r ${path.module}/function-code/requirements.txt -t ${path.module}/function-code"
  }
}

# Create a zip of the lambda function and its dependencies
data "archive_file" "crypto_alerts_zip" {
  type        = "zip"
  output_path = "crypto-${var.cryptocurrency}${var.name_postfix}.zip"
  source_dir  = "${path.module}/function-code/"
  excludes    = ["pyenv", ".idea", ".gitignore"]

  depends_on = [null_resource.pip]
}

# Deploy the AWS Lambda function
resource "aws_lambda_function" "crypto_alerts" {
  filename         = data.archive_file.crypto_alerts_zip.output_path
  function_name    = "crypto-${var.cryptocurrency}${var.name_postfix}"
  role             = aws_iam_role.crypto_alerts_lambda.arn
  handler          = "crypto_alerts.lambda_handler"
  source_code_hash = data.archive_file.crypto_alerts_zip.output_base64sha256
  runtime          = "python3.6"
  timeout          = 300
  publish          = true

  environment {
    variables = {
      BOT_NAME            = "crypto-${var.cryptocurrency}${var.name_postfix}"
      CRYPTOCURRENCY      = var.cryptocurrency
      ALERT_PRICE         = var.minimum_value
      COINBASE_API_KEY    = var.coinbase_api_key
      COINBASE_API_SECRET = var.coinbase_api_secret
      DISCORD_WEBHOOK_URL = var.discord_webhook_url
      DYNAMO_DB           = var.dynamodb
      ALERT_RATE_LIMIT    = var.alert_rate_limit
    }
  }
  tags = var.tags
}

# CloudWatch cron to run every X minutes
resource "aws_cloudwatch_event_rule" "crypto_alerts_cron" {
  name                = "crypto-${var.cryptocurrency}${var.name_postfix}"
  description         = "Fires every ${var.rate} minutes"
  schedule_expression = "rate(${var.rate} minutes)"
}

# CloudWatch event target for the Lambda
resource "aws_cloudwatch_event_target" "crypto_alerts_cron" {
  rule      = aws_cloudwatch_event_rule.crypto_alerts_cron.name
  target_id = "crypto-${var.cryptocurrency}${var.name_postfix}"
  arn       = aws_lambda_function.crypto_alerts.arn
}

# Grant CloudWatch permission to run the Lambda
resource "aws_lambda_permission" "crypto_alerts_allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.crypto_alerts.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.crypto_alerts_cron.arn
}
