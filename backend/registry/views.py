"""View handlers for RegistryManager"""
import re
import logging
import docker
from django.http import JsonResponse
from django.views import View
from api.common import RESPONSE
from config import DOCKER_ADDRESS, REGISTRY_ADDRESS

LOGGER = logging.getLogger(__name__)

class RegistryHandler:
    def __init__(self):
        self.client = docker.DockerClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)
        self.docker_api = docker.APIClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)

def docker_connection(address=None):
    registry = RegistryHandler()
    try:
        client_test = registry.client
        docker_api_test = registry.docker_api
        if address is not None:
            client_test = docker.DockerClient(base_url=address, tls=False)
            docker_api_test = docker.APIClient(base_url=address, tls=False)
        client_test.ping()
        docker_api_test.ping()
        return True
    except Exception:
        return False

class DockerfileHandler(View):
    http_method_names = ['post']
    registry = RegistryHandler()

    def post(self, request, **kwargs):
        """
        @api {post} /image_registry/dockerfile Upload a Dockerfile
        @apiName UploadDockerfile
        @apiGroup RegistryManager
        @apiVersion 0.1.0
        @apiParamExample {json} Request-Body-Example:
        {
            "file": fileObj
        }
        @apiParam {Object} The Dockerfile to be uploaded
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        """
        try:
            if not request.FILES:
                return JsonResponse(RESPONSE.INVALID_REQUEST)
            paramfile = request.FILES['file'].read().decode()
            f = request.FILES['file']
            dockerfile_pattern = "Dockerfile"
            searched_dockerfile = re.search(dockerfile_pattern, f.name, re.M|re.I)
            if searched_dockerfile:
                try:
                    image = self.registry.client.images.build(fileobj=paramfile, custom_context=True)[0]
                    name = image.tags[0]
                    newName = REGISTRY_ADDRESS + '/' + name
                    self.registry.docker_api.tag(name, newName)
                    self.registry.docker_api.push(newName)
                    return JsonResponse(RESPONSE.SUCCESS)
                except docker.errors.DockerException as e:
                    response = RESPONSE.SERVER_ERROR
                    response['message'] += str(e)
                    return JsonResponse(response)
        except Exception as e:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += str(e)
            return JsonResponse(response)
        return JsonResponse(RESPONSE.NOT_IMPLEMENTED)

class ImageHandler(View):
    http_method_names = ['post']
    registry = RegistryHandler()

    def post(self, request, **kwargs):
        """
        @api {post} /image_registry/image Upload image.tar
        @apiName UploadImageTar
        @apiGroup RegistryManager
        @apiVersion 0.1.0
        @apiParamExample {json} Request-Body-Example:
        {
            "file": fileObj
        }
        @apiParam {Object} The image.tar file to be uploaded
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        """
        try:
            if not request.FILES:
                return JsonResponse(RESPONSE.INVALID_REQUEST)
            f = request.FILES['file']
            tar_pattern = "[.](tar)$"
            searched_tar = re.search(tar_pattern, f.name, re.M|re.I)
            if searched_tar:
                try:
                    image = self.registry.client.images.load(f)[0]
                    name = image.tags[0]
                    newName = REGISTRY_ADDRESS + '/' + name
                    self.registry.docker_api.tag(name, newName)
                    self.registry.docker_api.push(newName)
                    return JsonResponse(RESPONSE.SUCCESS)
                except docker.errors.DockerException as e:
                    response = RESPONSE.SERVER_ERROR
                    response['payload']['docker exception'] = str(e)
                    return JsonResponse(response)
        except Exception as e:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += str(e)
            return JsonResponse(response)
        return JsonResponse(RESPONSE.NOT_IMPLEMENTED)
