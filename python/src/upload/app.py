import base64
import boto3
import json
import os
import traceback
from flask import Flask, request, jsonify

app = Flask(__name__)

s3 = boto3.client('s3')
sqs = boto3.client('sqs')

# ssm = boto3.client('ssm')
# def get_param(name):
#     return ssm.get_parameter(Name=name, WithDecryption=True)['Parameter']['Value']

# S3_BUCKET = get_param('/video_to_mp3/S3/BUCKET_NAME')
# SQS_QUEUE_URL = get_param('/video_to_mp3/SQS/QUEUE_URL')

S3_BUCKET = os.getenv('S3_BUCKET')
SQS_QUEUE_URL = os.getenv('SQS_QUEUE_URL')

@app.route('/upload', methods=['POST'])
def upload():
  try:
    # Get user email from custom header set by Lambda authorizer
    user_email = request.headers.get('X-User-Email')
    if not user_email:
      return 'Unauthorized', 401

    # Get uploaded file
    if 'file' not in request.files:
      return 'No file uploaded', 400
    
    file = request.files['file']
    filename = file.filename.strip()

    if not filename:
      return 'Filename is required', 400

    # Upload to S3
    s3.put_object(Bucket=S3_BUCKET, Key=f'{user_email}/raw/{filename}', Body=file_bytes)

    # Send message to SQS
    message = {
      'filename': filename,
      'user_email': user_email
    }
    sqs.send_message(
      QueueUrl=SQS_QUEUE_URL,
      MessageBody=json.dumps(message)
    )

    return 'File uploaded', 200

  except Exception as e:
    tb = traceback.format_exc()
    print(f'Error processing request: {str(e)}\nTraceback:\n{tb}\nEvent: {request.data.decode('utf-8')}')

    return 'An internal error occurred. Please try again later.', 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)