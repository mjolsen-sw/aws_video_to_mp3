import jwt, datetime, os
from flask import Flask, request
from psycopg2

server = Flask(__name__)

# config
CONNECTION_URL = os.getenv('CONNECTION_URL')

def get_pg_connection():
  return psycopg2.connect(CONNECTION_URL)

@server.route('/login', methods=['POST'])
def login():
  auth = request.authorization
  if not auth:
    return {'message': 'Missing credentials'}, 401
  
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
      return {'message': 'Invalid credentials'}, 401
    else:
      return createJWT(auth.username, os.getenv('JWT_SECRET'), True)
  else:
    return {'message': 'Invalid credentials'}, 401
  
@server.route('/validate', methods=['POST'])
def validate():
  encoded_jwt = request.headers.get('Authorization')

  if not encoded_jwt or not encoded_jwt.startswith('Bearer '):
    return {'message': 'Missing or invalid token'}, 401
  
  encoded_jwt = encoded_jwt.split(' ')[1]
  try:
    decoded_jwt = jwt.decode(encoded_jwt, os.getenv('JWT_SECRET'), algorithms=['HS256'])
    return decoded_jwt, 200
  except jwt.ExpiredSignatureError:
    return {'message': 'Token has expired'}, 401
  except jwt.InvalidTokenError:
    return {'message': 'Invalid token'}, 401
  
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
  server.run(host='0.0.0.0', port=5000, debug=True)