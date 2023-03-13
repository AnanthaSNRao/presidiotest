
from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import InMemoryUploadedFile
from .views import get, download
from unittest.mock import patch, MagicMock
from django.core.files.base import ContentFile
import boto3
from moto import mock_s3, mock_dynamodb
from .stoage_db import handler, upload
from decouple import config
from django.conf import settings


class PostS3ViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get(self):
        # Test POST request with a valid file
        data = {
        'my_file': InMemoryUploadedFile(ContentFile('example text'), None, 'test.txt', 'text/plain', len('example text'), None)
        }
        request = self.factory.post('/myview/', data=data)
        with patch('postS3.views.stoage_db.upload', return_value=True) as mock_upload:
             with patch('postS3.views.logger') as mock_logger:
                response = get(request)
                self.assertEqual(response.status_code, 200)
            # self.assertContains(response.content, 'File uploaded successfully.')
            # mock_upload.assert_called_once_with(data['my_file'])

        # Test POST request with no file
        data = {}
        request = self.factory.post('/myview/', data=data)
        with patch('postS3.views.logger') as mock_logger:
            response = get(request)
            self.assertEqual(response.status_code, 400)
        # self.assertContains(response.content, 'Please select a file.')

        # Test POST request with an invalid file type
        data = {
        'my_file': InMemoryUploadedFile(ContentFile('example text'), None, 'test.png', 'png/image', len('example text'), None)
        }
        request = self.factory.post('/myview/', data=data)
        with patch('postS3.views.logger') as mock_logger:
            response = get(request)
            self.assertEqual(response.status_code, 400)
        # self.assertContains(response, 'Invalid file type. Only text files are allowed.')

        # Test POST request with a file that fails to upload
        data = {
        'my_file': InMemoryUploadedFile(ContentFile('example text'), None, 'test.txt', 'text/plain', len('example text'), None)
        }
        request = self.factory.post('/myview/', data=data)
        with patch('postS3.views.stoage_db.upload', return_value=False) as mock_upload:
            response = get(request)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'File upload was not successful.')
            # mock_upload.assert_called_once_with(data['my_file'])



    def test_download(self):
        # Mock the handler function from storage_db module
        with patch('postS3.views.stoage_db.handler') as mock_handler:
            mock_handler.return_value = 'http://example.com/file.txt'
            
            # Test GET request
            request = self.factory.get('/download/')
            response = download(request)
            self.assertEqual(response.status_code, 200)
            # self.assertTemplateUsed(response, 'form.html')
            self.assertContains(response, 'http://example.com/file.txt')

        with patch('postS3.views.stoage_db.handler') as mock_handler:
            mock_handler.return_value = None
            
            # Test GET request with no file available
            request = self.factory.get('/download/')
            response = download(request)
            self.assertEqual(response.status_code, 404)
            # self.assertTemplateUsed(response, 'form.html')
            # self.assertContains(response, 'No file available for download.')




class StorageDBTest(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.f = open(str(settings.BASE_DIR) + '/static/test_data.txt', 'r')

    @mock_s3
    @mock_dynamodb    
    def test_handler(self):
        self.S3conn = boto3.resource("s3", region_name= config('AWS_REGION_NAME'))
        location = {'LocationConstraint': config('AWS_REGION_NAME')}
        # We need to create the bucket since this is all in Moto's 'virtual' AWS account
        self.S3conn.create_bucket(Bucket= config('OUTPUT_BUCKET'), CreateBucketConfiguration=location)

        self.dbcon = boto3.resource('dynamodb',  region_name= config('AWS_REGION_NAME'))
        self.table = self.dbcon.create_table(
            TableName=config('TABLE_NAME'),
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        self.table.put_item(Item ={"id":'1' ,"name": "foo"})
        url = handler()
        self.assertEqual(url, "https://s3-us-west-1.amazonaws.com/long-term-storage-presidio/lts-Presidio")
    
    @mock_s3 
    def test_upload(self):
        self.S3conn = boto3.resource("s3", region_name= config('AWS_REGION_NAME'))
        location = {'LocationConstraint': config('AWS_REGION_NAME')}
        # We need to create the bucket since this is all in Moto's 'virtual' AWS account
        self.S3conn.create_bucket(Bucket= config('INITIAL_S3_BUCKET_NAME'), CreateBucketConfiguration=location)
        res = upload(self.f)
        self.assertEqual(res, True)