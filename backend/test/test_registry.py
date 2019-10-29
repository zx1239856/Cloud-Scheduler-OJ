"""
Unit Test for Registry
"""
import os
import json
import docker
import mock
from django.test import TestCase, Client
from api.common import RESPONSE
import registry_manager.views as registry_views
import registry_manager.manifest as manifest_views
from .common import MockRequest, MockUrlOpen, MockDXFBase, MockDXF

class TestRegistryHandler_get(TestCase):
    def setUp(self):
        self.url = '/registry/'
        self.client = Client()
        self.local_client = docker.from_env()

    # @mock.patch.object(registry_views, 'Request', MockRequest)
    # @mock.patch.object(registry_views, 'urlopen', MockUrlOpen)
    # @mock.patch.object(registry_views, 'DXFBase', MockDXFBase)
    # @mock.patch.object(registry_views, 'DXF', MockDXF)
    def test_RegistryHandler_get(self):
        response = self.client.get('/registry/')
        resp = json.loads(response.content)
        # self.assertEqual(resp['payload']['entity'], [])
        self.assertContains(response=response, text='entity')

    def test_RepositoryHandler_get(self):
        response = self.client.get('/registry/ubuntu/')
        resp = json.loads(response.content)
        self.assertEquals('entity' in resp['payload'], True)

    # def test_dockerfile_upload1(self):
    #     url = self.url + 'dockerfile/'
    #     filename = 'Dockerfile'
    #     f = open('Dockerfile', 'w')
    #     f.write('FROM hello-world')
    #     f.close()
    #     f = open('Dockerfile', 'r')
    #     response = self.client.post(url, data={'file': f})
    #     f.close()
    #     os.remove(filename)
    #     self.assertEqual(response.status_code, 200)
    #     response = json.loads(response.content)
    #     # self.assertEqual(response['message'], RESPONSE.SUCCESS['message'])
    #     self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    # def test_dockerfile_upload2(self):
    #     url = self.url + 'dockerfile/'
    #     filename = 'Dockerfile'
    #     f = open(filename, 'w')
    #     f.close()
    #     f = open(filename, 'r')
    #     response = self.client.post(url, data={'file': f})
    #     f.close()
    #     os.remove(filename)
    #     self.assertEqual(response.status_code, 200)
    #     response = json.loads(response.content)
    #     # self.assertEqual(response['message'], RESPONSE.SERVER_ERROR['message'])
    #     self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    # def test_dockerfile_upload3(self):
    #     url = self.url + 'dockerfile/'
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, 200)
    #     response = json.loads(response.content)
    #     self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    # # def test_dockerfile_upload4(self):
    # #     url = self.url + 'dockerfile/'
    # #     filename = 'Dockerfile'
    # #     f = open(filename, 'w')
    # #     f.write("FROM hello-world")
    # #     f.close()
    # #     f = open(filename, 'r')
    # #     response = self.client.post(url, data={'file': f})
    # #     f.close()
    # #     os.remove(filename)
    # #     self.assertEqual(response.status_code, 200)
    # #     response = json.loads(response.content)
    # #     self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    # def test_image_upload1(self):
    #     url = self.url + 'image/'
    #     imagename = 'hello-world'
    #     filename = 'hello-world.tar'
    #     registry_views.client.images.pull(imagename)
    #     image = registry_views.docker_api.get_image(imagename)
    #     f = open(filename, 'wb+')
    #     for chunk in image:
    #         f.write(chunk)
    #     f.close()
    #     f = open(filename, 'rb+')
    #     response = self.client.post(url, data={'file': f})
    #     f.close()
    #     os.remove(filename)
    #     self.assertEqual(response.status_code, 200)
    #     response = json.loads(response.content)
    #     self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    # def test_image_upload2(self):
    #     url = self.url + 'image/'
    #     filename = 'hello-world.tar'
    #     f = open(filename, 'wb+')
    #     f.close()
    #     f = open(filename, 'rb+')
    #     response = self.client.post(url, data={'file': f})
    #     f.close()
    #     os.remove(filename)
    #     self.assertEqual(response.status_code, 200)
    #     response = json.loads(response.content)
    #     self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])

    # def test_image_upload3(self):
    #     url = self.url + 'image/'
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, 200)
    #     response = json.loads(response.content)
    #     self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    # # def test_image_upload4(self):
    # #     url = self.url + 'image/'
    # #     imagename = 'hello-world'
    # #     filename = 'hello-world.tar'
    # #     registry_views.client.images.pull(imagename)
    # #     image = registry_views.docker_api.get_image(imagename)
    # #     f = open(filename, 'wb+')
    # #     for chunk in image:
    # #         f.write(chunk)
    # #     f.close()
    # #     f = open(filename, 'r')
    # #     response = self.client.post(url, data={'file': f})
    # #     f.close()
    # #     os.remove(filename)
    # #     self.assertEqual(response.status_code, 200)
    # #     response = json.loads(response.content)
    # #     self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])
