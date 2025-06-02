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