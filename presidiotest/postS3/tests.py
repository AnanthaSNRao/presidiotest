
from django.test import TestCase, RequestFactory
from django.core.files.uploadedfile import InMemoryUploadedFile
from .views import get, download
from unittest.mock import patch, MagicMock
from django.core.files.base import ContentFile


class MyViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_get(self):
        # Test POST request with a valid file
        data = {
        'my_file': InMemoryUploadedFile(ContentFile('example text'), None, 'test.txt', 'text/plain', len('example text'), None)
        }
        request = self.factory.post('/myview/', data=data)
        with patch('postS3.views.stoage_db.upload', return_value=True) as mock_upload:
            response = get(request)
            self.assertEqual(response.status_code, 200)
            # self.assertContains(response.content, 'File uploaded successfully.')
            # mock_upload.assert_called_once_with(data['my_file'])

        # Test POST request with no file
        data = {}
        request = self.factory.post('/myview/', data=data)
        response = get(request)
        self.assertEqual(response.status_code, 400)
        # self.assertContains(response.content, 'Please select a file.')

        # Test POST request with an invalid file type
        data = {
        'my_file': InMemoryUploadedFile(ContentFile('example text'), None, 'test.png', 'png/image', len('example text'), None)
        }
        request = self.factory.post('/myview/', data=data)
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
