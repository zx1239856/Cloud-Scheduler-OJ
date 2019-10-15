"""
Unit Test for Registry
"""
import json
from django.test import TestCase, Client

class TestRegistry(TestCase):
    def setUp(self):
        self.url = '/image_registry/'
        self.client = Client()

    def test_upload_dockerfile(self):
        with open('test/testfiles/correct/Dockerfile', 'rb') as fp:
            response = self.client.post(self.url, data={'file': fp})
            json_resp = json.loads(response.content)
            self.assertEqual(json_resp['result'], "OK")
            self.assertTrue('filename' in json_resp)

    def test_upload_tar(self):
        with open('test/testfiles/correct/hello-world.tar', 'rb') as fp:
            response = self.client.post(self.url, data={'file': fp})
            json_resp = json.loads(response.content)
            self.assertEqual(json_resp['result'], "OK")
            self.assertTrue('filename' in json_resp)

    def test_upload_wrong_file(self):
        with open('test/testfiles/error/tmp.txt', 'rb') as fp:
            response = self.client.post(self.url, data={'file': fp})
            json_resp = json.loads(response.content)
            self.assertTrue('result' in json_resp)

    def test_upload_error_file(self):
        with open('test/testfiles/error/Dockerfile', 'rb') as fp:
            response = self.client.post(self.url, data={'file': fp})
            json_resp = json.loads(response.content)
            self.assertTrue('docker error' in json_resp)
        with open('test/testfiles/error/hello-world.tar', 'rb') as fp:
            response = self.client.post(self.url, data={'file': fp})
            json_resp = json.loads(response.content)
            self.assertTrue('docker error' in json_resp)
