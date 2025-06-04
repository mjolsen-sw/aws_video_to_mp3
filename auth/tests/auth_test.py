import datetime
import jwt
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import app

class AuthAppTestCase(unittest.TestCase):
  def setUp(self):
    app.app.config['TESTING'] = True
    app.JWT_SECRET = 'testsecret'
    self.client = app.app.test_client()
    self.jwt_secret = 'testsecret'
    self.username = 'test@example.com'
    self.password = 'testpass'

  @patch('app.get_pg_connection')
  def test_login_success(self, mock_get_pg_connection):
    # Mock DB cursor and connection
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [
      (self.username, self.password),  # user_row
    ]
    mock_get_pg_connection.return_value = mock_conn

    response = self.client.post(
      '/login',
      headers={
        'Authorization': 'Basic dGVzdEBleGFtcGxlLmNvbTp0ZXN0cGFzcw=='  # base64 for test@example.com:testpass
      }
    )
    self.assertEqual(response.status_code, 200)
    token = response.get_data(as_text=True)
    decoded = jwt.decode(token, app.JWT_SECRET, algorithms=['HS256'])
    self.assertEqual(decoded['username'], self.username)
    self.assertTrue(decoded['admin'])

  @patch('app.get_pg_connection')
  def test_login_missing_credentials(self, mock_get_pg_connection):
    response = self.client.post('/login')
    self.assertEqual(response.status_code, 401)
    self.assertIn('Missing credentials', response.get_data(as_text=True))

  @patch('app.get_pg_connection')
  def test_login_invalid_credentials(self, mock_get_pg_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [
        (self.username, self.password),  # user_row
    ]
    mock_get_pg_connection.return_value = mock_conn

    # Wrong password
    response = self.client.post(
      '/login',
      headers={
        'Authorization': 'Basic dGVzdEBleGFtcGxlLmNvbTp3cm9uZ3Bhc3M='  # base64 for test@example.com:wrongpass
      }
    )
    self.assertEqual(response.status_code, 401)
    self.assertIn('Invalid credentials', response.get_data(as_text=True))

  def test_validate_success(self):
    token = jwt.encode(
      {
        'username': self.username,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'admin': True
      },
      app.JWT_SECRET,
      algorithm='HS256'
    )
    response = self.client.post(
      '/validate',
      headers={'Authorization': f'Bearer {token}'}
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn(self.username, response.get_data(as_text=True))

  def test_validate_missing_token(self):
    response = self.client.post('/validate')
    self.assertEqual(response.status_code, 401)
    self.assertIn('Missing or invalid token', response.get_data(as_text=True))

  def test_validate_invalid_token(self):
    response = self.client.post(
      '/validate',
      headers={'Authorization': 'Bearer invalidtoken'}
    )
    self.assertEqual(response.status_code, 401)
    self.assertIn('Invalid token', response.get_data(as_text=True))

  def test_validate_expired_token(self):
    expired_token = jwt.encode(
      {
        'username': self.username,
        'exp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1),
        'iat': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2),
        'admin': True
      },
      app.JWT_SECRET,
      algorithm='HS256'
    )
    response = self.client.post(
      '/validate',
      headers={'Authorization': f'Bearer {expired_token}'}
    )
    self.assertEqual(response.status_code, 401)
    self.assertIn('Token has expired', response.get_data(as_text=True))

if __name__ == '__main__':
  unittest.main()