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
  name               = "crypto-${var.cryptocurrency}${var.name_postfix}-lambda"
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
  name        = "crypto-${var.cryptocurrency}${var.name_postfix}-lambda-logging"
  description = "Standard CloudWatch permissions for crypto-alerts-${var.cryptocurrency}-lambda"
  policy      = data.aws_iam_policy_document.crypto_alerts_lambda_logging.json
}

# Attach the CloudWatch Logging permissions
resource "aws_iam_policy_attachment" "crypto_alerts_lambda_logging" {
  name       = "crypto-${var.cryptocurrency}${var.name_postfix}-lambda-logging"
  roles      = [aws_iam_role.crypto_alerts_lambda.name]
  policy_arn = aws_iam_policy.crypto_alerts_lambda_logging.arn
}

# Conditional IAM Policy for DynamoDB
data "aws_iam_policy_document" "crypto_alerts_lambda_dynamodb" {
  count = var.dynamodb ? 1 : 0
  statement {
    sid = "ListAndDescribe"
    actions = ["dynamodb:List*",
      "dynamodb:DescribeReservedCapacity*",
      "dynamodb:DescribeLimits",
    "dynamodb:DescribeTimeToLive"]

    resources = ["*"]
    effect    = "Allow"
  }
  statement {
    sid = "AccessBotTable"
    actions = ["dynamodb:BatchGet*",
      "dynamodb:DescribeStream",
      "dynamodb:DescribeTable",
      "dynamodb:Get*",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:BatchWrite*",
      "dynamodb:CreateTable",
      "dynamodb:Delete*",
      "dynamodb:Update*",
    "dynamodb:PutItem"]

    resources = ["arn:aws:dynamodb:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:table/crypto-alerts"]
    effect    = "Allow"
  }
}

# Create the IAM policy for DynamoDB
resource "aws_iam_policy" "crypto_alerts_lambda_dynamodb" {
  count       = var.dynamodb ? 1 : 0
  name        = "crypto-${var.cryptocurrency}${var.name_postfix}-dynamodb"
  description = "Update last alert times in DynamoDB for crypto-alerts-${var.cryptocurrency}-lambda"
  policy      = data.aws_iam_policy_document.crypto_alerts_lambda_dynamodb[count.index].json
}

# Attach the DynamoDB permissions
resource "aws_iam_policy_attachment" "crypto_alerts_lambda_dynamodb" {
  count      = var.dynamodb ? 1 : 0
  name       = "crypto-${var.cryptocurrency}${var.name_postfix}-dynamodb"
  roles      = [aws_iam_role.crypto_alerts_lambda.name]
  policy_arn = aws_iam_policy.crypto_alerts_lambda_dynamodb[count.index].arn
}
