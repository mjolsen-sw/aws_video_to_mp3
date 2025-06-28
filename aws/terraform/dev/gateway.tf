resource "aws_api_gateway_rest_api" "main" {
  name        = "video-to-mp3-api"
  description = "API Gateway for Video to MP3"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_lambda_permission" "apigw_auth" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.authorizer.function_name
  principal     = "apigateway.amazonaws.com"
}

resource "aws_api_gateway_authorizer" "lambda" {
  name                   = "lambda-authorizer"
  rest_api_id            = aws_api_gateway_rest_api.main.id
  authorizer_uri         = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.authorizer.arn}/invocations"
  authorizer_result_ttl_in_seconds = 300
  identity_source        = "method.request.header.Authorization"
  type                   = "TOKEN"
}

resource "aws_api_gateway_method" "proxy_any" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.lambda.id
  request_parameters = {
    "method.request.path.proxy" = true
    "method.request.header.Authorization" = true
  }
}

resource "aws_api_gateway_integration" "alb_proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_any.http_method
  type        = "HTTP_PROXY"
  integration_http_method = "ANY"
  uri         = "http://${aws_lb.private_alb.dns_name}/{proxy}"
  passthrough_behavior = "WHEN_NO_MATCH"
  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
    "integration.request.header.X-User-Email" = "context.authorizer.X-User-Email"
  }
}

resource "aws_api_gateway_deployment" "main" {
  depends_on = [aws_api_gateway_integration.alb_proxy]
  rest_api_id = aws_api_gateway_rest_api.main.id
}

resource "aws_lambda_function" "authorizer" {
  function_name = "video-to-mp3-authorizer"
  handler       = "authorizer.lambda_handler"
  runtime       = "python3.12"
  role          = aws_iam_role.lambda_authorizer_role.arn

  filename      = "../../lambdas/authorizer/authorizer.zip"

  # Optionally, set environment variables, timeout, etc.
  environment {
    variables = {
      FLASK_AUTH_URL = var.flask_auth_url
    }
  }
}

resource "aws_iam_role" "lambda_authorizer_role" {
  name = "lambda-authorizer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_authorizer_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Output the invoke URL
output "api_invoke_url" {
  value = "${aws_api_gateway_deployment.main.invoke_url}"
}