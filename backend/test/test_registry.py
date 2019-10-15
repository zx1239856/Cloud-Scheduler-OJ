"""
Unit Test for Registry
"""
from io import BytesIO
import mock
from django.test import TestCase, Client

def create_dockerfile(file_path):
    with open('/data/'+file_path) as f:
        return f.read()

class TestRegistry(TestCase):
    def setUp(self):
        self.url = '/image_registry/'
        self.client = Client()

    @mock.patch("registry.views.DockerfileHandler.post", create=True)
    def test_dockerfile_upload(self, mock_open):
        url = self.url + 'dockerfile/'
        with mock.patch('__main__.open', mock_open(read_data='dockerfile')) as m:
            response = self.client.post(url, data={'file': m})
            self.assertTrue(response.status_code, 200)

        dockerfile = BytesIO()
        dockerfile.name = 'Dockerfile'
        response = self.client.post(url, {'file': dockerfile})
        # self.assertTrue(response.context, 'dat')
        # json_resp = json.loads(response.content)
        self.assertTrue(response.status_code, 200)
        # self.assertTrue('data' in json_resp)
        # with mock.patch('__main__.open', mock_open(read_data='dockerfile')) as m:
        #     response = self.client.post(url, data={'file': m}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        #     self.assertEqual(response.status_code, 200)
            # json_resp = json.loads(response.data)
            # self.assertTrue('condition' in json_resp)

    @mock.patch("registry.views.ImageHandler.post", create=True)
    def test_image_upload(self, mock_open):
        url = self.url + 'image/'
        with mock.patch('__main__.open', mock_open(read_data='image')) as m:
            response = self.client.post(url, data={'file': m})
            self.assertTrue(response.status_code, 200)

    # def test_upload_file(self):
    #     with open('test/testfiles/Dockerfile', 'rb') as fp:
    #         response = self.client.post(self.url, data={'file': fp})
    #         json_resp = json.loads(response.content)
    #         self.assertEqual(json_resp['condition'], "OK")
    #         self.assertTrue('filename' in json_resp)
