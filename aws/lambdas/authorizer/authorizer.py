import os
import json
import requests

FLASK_AUTH_URL = os.environ.get("FLASK_AUTH_URL")

def lambda_handler(event, context):
  # Extract the JWT token from the Authorization header
  token = event['headers'].get('Authorization')
  if not token:
    return generate_policy('anonymous', 'Deny', event['methodArn'])

  # Call the Flask /validate endpoint
  try:
    resp = requests.post(
      FLASK_VALIDATE_URL,
      headers={'Authorization': token},
      timeout=3
    )
  except Exception as e:
    print(f"Error calling Flask validate: {e}")
    return generate_policy('anonymous', 'Deny', event['methodArn'])

  if resp.status_code != 200:
    return generate_policy('anonymous', 'Deny', event['methodArn'])

  claims = resp.json()
  user_email = claims.get('username')
  if not user_email:
    return generate_policy('anonymous', 'Deny', event['methodArn'])

  # Success: allow and set context for downstream
  return {
    "principalId": user_email,
    "policyDocument": {
      "Version": "2012-10-17",
      "Statement": [{
        "Action": "execute-api:Invoke",
        "Effect": "Allow",
        "Resource": event['methodArn']
      }]
    },
    "context": {
      "X-User-Email": user_email
    }
  }

def generate_policy(principal_id, effect, resource):
  return {
    "principalId": principal_id,
    "policyDocument": {
      "Version": "2012-10-17",
      "Statement": [{
        "Action": "execute-api:Invoke",
        "Effect": effect,
        "Resource": resource
      }]
    }
  }