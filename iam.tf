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

### Standard Lambda@Edge ###

# IAM role for the crypto-alerts Lambda to assume role
resource "aws_iam_role" "crypto_alerts_lambda" {
  name               = "crypto-${var.cryptocurrency}-${var.name_postfix}-lambda"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": [
          "lambda.amazonaws.com",
          "edgelambda.amazonaws.com"
        ]
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

# Attach the Basic Execution permissions
resource "aws_iam_role_policy_attachment" "crypto_alerts_lambda" {
  role       = aws_iam_role.crypto_alerts_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# IAM Policy for AWS CloudWatch logging
data "aws_iam_policy_document" "crypto_alerts_lambda_logging" {
  statement {
    sid = "CloudWatchLogging"
    actions = ["logs:CreateLogGroup",
      "logs:CreateLogStream",
    "logs:PutLogEvents"]

    resources = ["arn:aws:logs:*:*:*"]
    effect    = "Allow"
  }
}

# Create the IAM policy for CloudWatch logging
resource "aws_iam_policy" "crypto_alerts_lambda_logging" {
  name        = "crypto-${var.cryptocurrency}-${var.name_postfix}-lambda-logging"
  description = "Standard CloudWatch permissions for crypto-alerts-${var.cryptocurrency}-lambda"
  policy      = data.aws_iam_policy_document.crypto_alerts_lambda_logging.json
}

# Attach the CloudWatch Logging permissions
resource "aws_iam_policy_attachment" "crypto_alerts_lambda_logging" {
  name       = "crypto-${var.cryptocurrency}-${var.name_postfix}-lambda-logging"
  roles      = [aws_iam_role.crypto_alerts_lambda.name]
  policy_arn = aws_iam_policy.crypto_alerts_lambda_logging.arn
}
