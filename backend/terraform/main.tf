provider "aws" {
  region = "us-east-1"
}

# S3 Bucket for datasets and reports
resource "aws_s3_bucket" "datasets" {
  bucket = "ethicali-datasets"
}

# DynamoDB table for compliance logs
resource "aws_dynamodb_table" "compliance_logs" {
  name           = "ComplianceLogs"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "RecordID"

  attribute {
    name = "RecordID"
    type = "S"
  }
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "ethicali-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Effect = "Allow"
      Sid    = ""
    }]
  })
}

# Attach policies for S3, DynamoDB and CloudWatch logging
resource "aws_iam_role_policy_attachment" "lambda_s3" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_dynamo" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ✅ Lambda function
resource "aws_lambda_function" "dataset_validation" {
  filename         = "./../lambda/dataset_validation/lambda.zip"
  function_name    = "datasetValidation"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.11"
  role             = aws_iam_role.lambda_exec.arn
  timeout          = 10
}

# API Gateway
resource "aws_apigatewayv2_api" "http_api" {
  name          = "ethicali-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.dataset_validation.invoke_arn
}

resource "aws_apigatewayv2_route" "validate_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /validate-dataset"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_lambda_permission" "apigw_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dataset_validation.function_name
  principal     = "apigateway.amazonaws.com"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id = aws_apigatewayv2_api.http_api.id
  name   = "$default"
  auto_deploy = true
}

output "api_url" {
  value = aws_apigatewayv2_api.http_api.api_endpoint
}
