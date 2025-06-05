import io
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import app

class UploadAppTestCase(unittest.TestCase):
  def setUp(self):
    app.app.config['TESTING'] = True
    app.S3_BUCKET = 'test-bucket'
    app.SQS_QUEUE_URL = 'https://sqs.test'
    self.client = app.app.test_client()

  def test_upload_missing_user_email(self):
    data = {
      'file': (io.BytesIO(b'test content'), 'testfile.mp4')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      data=data
    )
    self.assertEqual(response.status_code, 401)
    self.assertIn('Unauthorized', response.get_data(as_text=True))

  def test_upload_no_file(self):
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data={}
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('Only one file can be uploaded at a time', response.get_data(as_text=True))

  def test_upload_multiple_files(self):
    data = {
      'file1': (io.BytesIO(b'content1'), 'file1.mp4'),
      'file2': (io.BytesIO(b'content2'), 'file2.mp4')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('Only one file can be uploaded at a time', response.get_data(as_text=True))

  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_empty_filename(self, mock_sqs, mock_s3):
    data = {
      'file': (io.BytesIO(b'test content'), '')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('Filename is required', response.get_data(as_text=True))
    mock_s3.put_object.assert_not_called()
    mock_sqs.send_message.assert_not_called()

  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_s3_exception(self, mock_sqs, mock_s3):
    mock_s3.put_object.side_effect = Exception('S3 error')
    data = {
      'file': (io.BytesIO(b'test content'), 'testfile.mp4')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 500)
    self.assertIn('An internal error occurred', response.get_data(as_text=True))

  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_sqs_exception(self, mock_sqs, mock_s3):
    mock_s3.put_object.return_value = {}
    mock_sqs.send_message.side_effect = Exception('SQS error')
    data = {
      'file': (io.BytesIO(b'test content'), 'testfile.mp4')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 500)
    self.assertIn('An internal error occurred', response.get_data(as_text=True))

  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_empty_file(self, mock_sqs, mock_s3):
    # Test when file is present but empty
    data = {
      'file': (io.BytesIO(b''), 'testfile.mp4')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('File is empty', response.get_data(as_text=True))
    mock_s3.put_object.assert_not_called()
    mock_sqs.send_message.assert_not_called()

  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_file_with_whitespace_content(self, mock_sqs, mock_s3):
    # Test when file contains only whitespace (should not be considered empty)
    mock_s3.put_object.return_value = {}
    mock_sqs.send_message.return_value = {}

    data = {
      'file': (io.BytesIO(b'   '), 'testfile.mp4')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('File is empty', response.get_data(as_text=True))
    mock_s3.put_object.assert_not_called()
    mock_sqs.send_message.assert_not_called()

  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_video_file_success(self, mock_sqs, mock_s3):
    mock_s3.put_object.return_value = {}
    mock_sqs.send_message.return_value = {}

    data = {
      'file': (io.BytesIO(b'video content'), 'video.mp4')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('File uploaded', response.get_data(as_text=True))

  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_non_video_file_rejected(self, mock_sqs, mock_s3):
    data = {
      'file': (io.BytesIO(b'not a video'), 'document.txt')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('Only video files are allowed', response.get_data(as_text=True))
    mock_s3.put_object.assert_not_called()
    mock_sqs.send_message.assert_not_called()
  
  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_uppercase_video_extension(self, mock_sqs, mock_s3):
    mock_s3.put_object.return_value = {}
    mock_sqs.send_message.return_value = {}

    data = {
      'file': (io.BytesIO(b'video content'), 'VIDEO.MP4')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('File uploaded', response.get_data(as_text=True))

  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_filename_with_spaces(self, mock_sqs, mock_s3):
    mock_s3.put_object.return_value = {}
    mock_sqs.send_message.return_value = {}

    data = {
      'file': (io.BytesIO(b'video content'), '  video.mp4  ')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('File uploaded', response.get_data(as_text=True))
  
  @patch('app.s3')
  @patch('app.sqs')
  def test_upload_audio_file_rejected(self, mock_sqs, mock_s3):
    data = {
      'file': (io.BytesIO(b'audio content'), 'audio.mp3')
    }
    response = self.client.post(
      '/upload',
      content_type='multipart/form-data',
      headers={'X-User-Email': 'user@example.com'},
      data=data
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('Only video files are allowed', response.get_data(as_text=True))
    mock_s3.put_object.assert_not_called()
    mock_sqs.send_message.assert_not_called()

if __name__ == '__main__':
  unittest.main()