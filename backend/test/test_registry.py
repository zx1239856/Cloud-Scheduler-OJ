"""
Unit Test for Registry
"""
import os
import json
import mock
from api.common import RESPONSE
import registry_manager.views as registry_views
from .common import MockRequest, MockUrlOpen, MockDXF, MockDXFBase, MockJsonRequest, MockGetTags, MockDockerClient, MockAPIClient, TestCaseWithBasicUser, login_test_user

class TestRegistryHandler(TestCaseWithBasicUser):
    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXFBase', MockDXFBase)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    def test_RegistryHandler_get(self):
        token = login_test_user('admin')
        response = self.client.get('/registry/', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(resp['payload']['entity'], [{'NumberOfTags': 1, 'Repo': 'test_repo', 'SizeOfRepository': 0}])

class TestRepositoryHander(TestCaseWithBasicUser):
    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    @mock.patch.object(registry_views.ConnectionUtils, 'get_tags', MockGetTags)
    def test_RepositoryHandler_get(self):
        token = login_test_user('admin')
        response = self.client.get('/registry/test_repo/', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
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
                    'Layers': 1,
                    'Size': 0,
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
        response = self.client.get('/registry/test_repo/', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
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
        response = self.client.post('/registry/upload/', data={'file[]': [f]}, HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
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
        response = self.client.post('/registry/upload/', data={}, HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
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
        response = self.client.delete('/registry/test/test/', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], RESPONSE.SUCCESS['status'])
