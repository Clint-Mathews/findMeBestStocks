# Define the variables in your main.tf
variable "aws_access_key" {
  description = "AWS Access Key"
}

variable "aws_secret_key" {
  description = "AWS Secret Access Key"
}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.0" 
    }
  }
}

provider "aws" {
  region     = "ap-south-1"
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "iam_for_lambda"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_lambda_function" "find_stock_lambda" {
  filename      = "find_trending_stocks_to_buy.zip"
  runtime       = "python3.8"
  function_name = "find_stocks_and_update"
  role          = aws_iam_role.iam_for_lambda.arn
  handler  = "find_trending_stocks_to_buy.handler"

  source_code_hash = data.archive_file.lambda.output_base64sha256
}
