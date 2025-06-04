import boto3
import datetime
import jwt
import os
import psycopg2
from flask import Flask, request

app = Flask(__name__)

# ssm = boto3.client('ssm')
# def get_param(name):
#     return ssm.get_parameter(Name=name, WithDecryption=True)['Parameter']['Value']

# CONNECTION_URL = get_param('/video_to_mp3/auth_db/CONNECTION_URL')
# JWT_SECRET = get_param('/video_to_mp3/auth/JWT_SECRET')

CONNECTION_URL = os.getenv('CONNECTION_URL')
JWT_SECRET = os.getenv('JWT_SECRET')

def get_pg_connection():
  return psycopg2.connect(CONNECTION_URL)

@app.route('/login', methods=['POST'])
def login():
  auth = request.authorization
  if not auth:
    return 'Missing credentials', 401
  
  conn = get_pg_connection()
  cur = conn.cursor()
  cur.execute(
    'SELECT email, password FROM users WHERE email=%s', (auth.username, )
  )
  user_row = cur.fetchone()
  cur.close()
  conn.close()

  if user_row:
    user_row = cur.fetchone()
    email, password = user_row

    if auth.username != email or auth.password != password:
      return 'Invalid credentials', 401
    else:
      return createJWT(auth.username, JWT_SECRET, True)
  else:
    return 'Invalid credentials', 401

@app.route('/validate', methods=['POST'])
def validate():
  encoded_jwt = request.headers.get('Authorization')

  if not encoded_jwt or not encoded_jwt.startswith('Bearer '):
    return 'Missing or invalid token', 401
  
  encoded_jwt = encoded_jwt.split(' ')[1]
  try:
    decoded_jwt = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=['HS256'])
    return decoded_jwt, 200
  except jwt.ExpiredSignatureError:
    return 'Token has expired', 401
  except jwt.InvalidTokenError:
    return 'Invalid token', 401
  
def createJWT(username, secret, is_admin):
  return jwt.encode(
    {
      'username': username,
      'exp': datetime.datetime.utcnow(tz=datetime.timezone.utc) + datetime.timedelta(days=1)
      'iat': datetime.datetime.utcnow(tz=datetime.timezone.utc),
      'admin': is_admin
    },
    secret,
    algorithm='HS256'
  )

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)