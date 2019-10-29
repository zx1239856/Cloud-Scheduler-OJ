"""
Unit Test for Registry
"""
import json
import mock
from django.test import TestCase
from api.common import RESPONSE
import registry_manager.views as registry_views
from .common import MockRequest, MockUrlOpen, MockDXF, MockDXFBase, MockJsonRequest, MockGetTags

class TestRegistryHandler(TestCase):
    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXFBase', MockDXFBase)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    def test_RegistryHandler_get(self):
        response = self.client.get('/registry/')
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(resp['payload']['entity'], [{'NumberOfTags': 1, 'Repo': 'test_repo', 'SizeOfRepository': 0}])

class TestRepositoryHander(TestCase):
    @mock.patch.object(registry_views, 'Request', MockRequest)
    @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    @mock.patch.object(registry_views, 'DXF', MockDXF)
    @mock.patch.object(registry_views.ConnectionUtils, 'json_request', MockJsonRequest)
    @mock.patch.object(registry_views.ConnectionUtils, 'get_tags', MockGetTags)
    def test_RepositoryHandler_get(self):
        response = self.client.get('/registry/test_repo/')
        resp = json.loads(response.content)
        self.assertEqual(resp['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(
            resp['payload']['entity'],
            [
                {
                    'Created': '2019-01-01T01:29:27.650294696Z',
                    'Docker Version': '18.06.1-ce',
                    'Entrypoint': None,
                    'Exposed Ports': None,
                    'Layers': 1,
                    'Size': 0,
                    'Tag': 'test_alias',
                    'Volumes': None
                }
            ]
        )

    # def test_RepositoryHandler_post(self):

    # def test_RepositoryHandler_delete_error1(self):
    #     response = self.client.delete('/registry/test/test/')
    #     resp = json.loads(response.content)
    #     self.assertEqual(resp['status'], RESPONSE.OPERATION_FAILED['status'])
