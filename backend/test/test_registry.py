"""
Unit Test for Registry
"""
import os
import json
import shutil
import mock
from api.common import RESPONSE
import registry_manager.views as registry_views
from registry_manager.models import ImageModel
from .common import MockRequest, MockUrlOpen, MockDXF, MockDXFBase, MockJsonRequest, MockGetTags, MockDockerClient, MockAPIClient, TestCaseWithBasicUser, login_test_user, MockUrlOpenErrorResponse

@mock.patch.object(registry_views, 'Request', MockRequest)
@mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
class TestRegistryHandler(TestCaseWithBasicUser):
    @mock.patch.object(registry_views, 'DXFBase', MockDXFBase)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    def test_RegistryHandler_get(self):
        token = login_test_user('admin')
        response = self.client.get('/registry/', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(resp['payload']['entity'], [{'Repo': 'test_repo'}])

class TestRepositoryHander(TestCaseWithBasicUser):

    def setUp(self):
        super().setUp()
        ImageModel.objects.create(filename='test', status=0, hashid='0')
        ImageModel.objects.create(filename='test', status=1, hashid='1')
        ImageModel.objects.create(filename='test', status=2, hashid='2')
        ImageModel.objects.create(filename='test', status=3, hashid='3')
        ImageModel.objects.create(filename='test', status=4, hashid='4')

    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    @mock.patch.object(registry_views.ConnectionUtils, 'get_tags', MockGetTags)
    def test_RepositoryHandler_get(self):
        token = login_test_user('admin')
        response = self.client.get('/registry/repository/test_repo/', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(
            resp['payload']['entity'],
            [
                {
                    'Created': '2019-01-01T01:29:27.650294696Z',
                    'DockerVersion': '18.06.1-ce',
                    'Entrypoint': 'null',
                    'ExposedPorts': 'null',
                    'Tag': 'test_alias',
                    'Volumes': 'null'
                }
            ]
        )

    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'get_tags', MockGetTags)
    def test_RepositoryHandler_get_2(self):
        token = login_test_user('admin')
        response = self.client.get('/registry/repository/test_repo/', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], RESPONSE.SUCCESS['status'])

    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    @mock.patch.object(registry_views.ConnectionUtils, 'get_tags', MockGetTags)
    @mock.patch.object(registry_views, 'DockerClient', MockDockerClient)
    @mock.patch.object(registry_views, 'APIClient', MockAPIClient)
    def test_RepositoryHandler_post(self):
        token = login_test_user('admin')
        f = open('test.tar', 'w')
        f.close()
        f = open('test.tar', 'r')
        response = self.client.post('/registry/repository/upload/', data={'file[]': [f]}, HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        f.close()
        os.remove('test.tar')

    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'get_tags', MockGetTags)
    @mock.patch.object(registry_views, 'DockerClient', MockDockerClient)
    @mock.patch.object(registry_views, 'APIClient', MockAPIClient)
    def test_RepositoryHandler_post_error1(self):
        token = login_test_user('admin')
        response = self.client.post('/registry/repository/upload/', data={}, HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    @mock.patch.object(registry_views.ConnectionUtils, 'get_tags', MockGetTags)
    def test_RepositoryHandler_delete(self):
        token = login_test_user('admin')
        response = self.client.delete('/registry/repository/test/test/', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], RESPONSE.SUCCESS['status'])

    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    @mock.patch.object(registry_views.ConnectionUtils, 'get_tags', MockGetTags)
    @mock.patch.object(registry_views, 'DockerClient', MockDockerClient)
    @mock.patch.object(registry_views, 'APIClient', MockAPIClient)
    def test_cacheFile(self):
        shutil.rmtree('registry_manager/data', ignore_errors=True)
        token = login_test_user('admin')
        f = open('test.tar', 'w')
        f.close()
        f = open('test.tar', 'r')
        response = self.client.post('/registry/repository/upload/', data={'file[]': [f]}, HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        f.close()
        os.remove('test.tar')

    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DockerClient', MockDockerClient)
    @mock.patch.object(registry_views, 'APIClient', MockAPIClient)
    def test_upload(self):
        registry_views.RepositoryHandler().upload("test.tar", 'testid')

    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpenErrorResponse)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    def test_get_tag_error(self):
        result = registry_views.ConnectionUtils().get_tag('test_repo', 'test_tag')
        self.assertEqual(result, None)

    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    def test_get_tags(self):
        result = registry_views.ConnectionUtils().get_tags('test_repo')
        self.assertEqual(['test_alias'], result)

class TestUploadHandler(TestCaseWithBasicUser):
    def test_get(self):
        token = login_test_user('admin')
        response = self.client.get('/registry/history/?page=1&limit=25', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    def test_get_error(self):
        token = login_test_user('admin')
        response = self.client.get('/registry/history/?page=-1&limit=25', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])
