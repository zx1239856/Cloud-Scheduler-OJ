"""
Unit Test for Registry
"""
import json
import mock
from django.test import TestCase, Client

# def file_content(file_path):
#     with open('/data/'+file_path) as f:
#         return f.read()

class TestRegistry(TestCase):
    def setUp(self):
        self.url = '/image_registry/'
        self.client = Client()

    @mock.patch("registry.views.post", create=True)
    def test_upload(self, mock_open):
        # testfile = mock.mock_open(read_data="Data").return_value

        with mock.patch('__main__.open', mock_open(read_data='bibble')) as m:
            response = self.client.post(self.url, data={'file': m})
            json_resp = json.loads(response.content)
            self.assertTrue('filename' in json_resp)
    # def test_upload_file(self):
    #     with open('test/testfiles/correct/Dockerfile', 'rb') as fp:
    #         response = self.client.post(self.url, data={'file': fp})
    #         json_resp = json.loads(response.content)
    #         self.assertEqual(json_resp['result'], "OK")
    #         self.assertTrue('filename' in json_resp)

    # def test_upload_tar(self):
    #     with open('test/testfiles/correct/hello-world.tar', 'rb') as fp:
    #         response = self.client.post(self.url, data={'file': fp})
    #         json_resp = json.loads(response.content)
    #         self.assertEqual(json_resp['result'], "OK")
    #         self.assertTrue('filename' in json_resp)

    # def test_upload_wrong_file(self):
    #     with open('test/testfiles/error/tmp.txt', 'rb') as fp:
    #         response = self.client.post(self.url, data={'file': fp})
    #         json_resp = json.loads(response.content)
    #         self.assertTrue('result' in json_resp)

    # def test_upload_error_file(self):
    #     with open('test/testfiles/error/Dockerfile', 'rb') as fp:
    #         response = self.client.post(self.url, data={'file': fp})
    #         json_resp = json.loads(response.content)
    #         self.assertTrue('docker error' in json_resp)
    #     with open('test/testfiles/error/hello-world.tar', 'rb') as fp:
    #         response = self.client.post(self.url, data={'file': fp})
    #         json_resp = json.loads(response.content)
    #         self.assertTrue('docker error' in json_resp)
