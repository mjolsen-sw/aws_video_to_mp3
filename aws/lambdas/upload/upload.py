import os
import boto3
import base64
import json

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

S3_BUCKET = os.environ['S3_BUCKET']
SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):
  try:
    # Get user email from authorizer claims
    claims = event['requestContext']['authorizer']['claims']
    user_email = claims.get('email')
    if not user_email:
      return {
        'statusCode': 401,
        'body': 'Unauthorized: Email claim not found'
      }

    # Expect JSON body with keys: filename, filecontent (base64)
    body = event.get('body')
    if event.get('isBase64Encoded'):
      body = base64.b64decode(body).decode('utf-8')
    data = json.loads(body)
    
    filename = data.get('filename')
    filecontent_b64 = data.get('filecontent')
    
    if not filename or not filecontent_b64:
      return {
        'statusCode': 400,
        'body': 'filename and filecontent are required'
      }
    
    # Decode file content from base64
    file_bytes = base64.b64decode(filecontent_b64)
    
    # Upload to S3
    s3.put_object(Bucket=S3_BUCKET, Key=f'{user_email}/raw/{filename}', Body=file_bytes)
    
    # Send message to SQS
    message = {
      'filename': filename,
      'user_email': user_email,
      'processed': False
    }
    sqs.send_message(
      QueueUrl=SQS_QUEUE_URL,
      MessageBody=json.dumps(message)
    )
    
    return {
      'statusCode': 200,
      'body': 'File uploaded'
    }
  
  except Exception as e:
    tb = traceback.format_exc()
    print(f'Error processing request: {str(e)}\nTraceback:\n{tb}\nEvent: {json.dumps(event)}')
    
    return {
      'statusCode': 500,
      'body': 'An internal error occurred. Please try again later.'
    }