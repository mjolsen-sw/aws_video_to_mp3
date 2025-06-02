import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
server.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
server.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
server.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
server.config['MYSQL_PORT'] = os.getenv('MYSQL_PORT', '3306')

@server.route('/login', methods=['POST'])
def login():
  auth = request.authorization
  if not auth:
    return {'message': 'Missing credentials'}, 401
  
  # check db for username and password
  cur = mysql.connection.cursor()
  res = cur.execute(
    'SELECT emaiul, password FROM user WHERE email=%s', (auth.username, )
  )

  if res > 0:
    user_row = cur.fetchone()
    email = user_row[0]
    password = user_row[1]

    if auth.username != email or auth.password != password:
      return {'message': 'Invalid credentials'}, 401
    else:
      return createJWT(auth.username, os.getenv('JWT_SECRET'), True)
  else:
    return {'message': 'Invalid credentials'}, 401