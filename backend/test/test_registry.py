"""
Unit Test for Registry
"""
import os
import json
import docker
from django.test import TestCase, Client
from api.common import RESPONSE
import registry.views as registry_views

class TestRegistry(TestCase):
    def setUp(self):
        self.url = '/image_registry/'
        self.client = Client()
        self.local_client = docker.from_env()

    def test_docker_is_running(self):
        self.assertEqual(registry_views.docker_connection(), True)

    def test_docker_error_connection(self):
        self.assertEqual(registry_views.docker_connection("https://registry.malform.address:30000"), False)

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

    def test_dockerfile_upload3(self):
        url = self.url + 'dockerfile/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    # def test_dockerfile_upload4(self):
    #     url = self.url + 'dockerfile/'
    #     filename = 'Dockerfile'
    #     f = open(filename, 'w')
    #     f.write("FROM hello-world")
    #     f.close()
    #     f = open(filename, 'r')
    #     response = self.client.post(url, data={'file': f})
    #     f.close()
    #     os.remove(filename)
    #     self.assertEqual(response.status_code, 200)
    #     response = json.loads(response.content)
    #     self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    # def test_image_upload1(self):
    #     url = self.url + 'image/'
    #     imagename = 'hello-world'
    #     filename = 'hello-world.tar'
    #     registry = registry_views.RegistryHandler()
    #     registry.client.images.pull(imagename)
    #     image = registry.docker_api.get_image(imagename)
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

    def test_image_upload2(self):
        url = self.url + 'image/'
        filename = 'hello-world.tar'
        f = open(filename, 'wb+')
        f.close()
        f = open(filename, 'rb+')
        response = self.client.post(url, data={'file': f})
        f.close()
        os.remove(filename)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])

    def test_image_upload3(self):
        url = self.url + 'image/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    # def test_image_upload4(self):
    #     url = self.url + 'image/'
    #     imagename = 'hello-world'
    #     filename = 'hello-world.tar'
    #     registry_views.client.images.pull(imagename)
    #     image = registry_views.docker_api.get_image(imagename)
    #     f = open(filename, 'wb+')
    #     for chunk in image:
    #         f.write(chunk)
    #     f.close()
    #     f = open(filename, 'r')
    #     response = self.client.post(url, data={'file': f})
    #     f.close()
    #     os.remove(filename)
    #     self.assertEqual(response.status_code, 200)
    #     response = json.loads(response.content)
    #     self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])
