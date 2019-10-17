"""View handlers for RegistryManager"""
import os
import re
import logging
import requests
import docker
from django.http import JsonResponse
from django.views import View
from api.common import RESPONSE
from config import DOCKER_ADDRESS, REGISTRY_ADDRESS

client = docker.DockerClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)
docker_api = docker.APIClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)
LOGGER = logging.getLogger(__name__)

# def test_docker_is_running():
#     try:
#         client.ping()
#         return True
#     except (requests.exceptions.ConnectionError, docker.errors.APIError):
#         return False

class DockerfileHandler(View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        try:
            if not request.FILES:
                return JsonResponse(RESPONSE.INVALID_REQUEST)
            f = request.FILES['file']
            file_name = ""
            path = "registry/data/"
            dockerfile_pattern = "Dockerfile"
            searched_dockerfile = re.search(dockerfile_pattern, f.name, re.M|re.I)
            if searched_dockerfile:
                try:
                    if not os.path.exists(path):
                        os.makedirs(path)
                    file_name = path + f.name
                    destination = open(file_name, 'wb+')
                    for chunk in f.chunks():
                        destination.write(chunk)
                    destination.close()
                    image = client.images.build(path='registry/data')[0]
                    name = image.tags[0]
                    newName = REGISTRY_ADDRESS + '/' + name
                    docker_api.tag(name, newName)
                    docker_api.push(newName)
                    return JsonResponse(RESPONSE.SUCCESS)
                except Exception as e:
                    return JsonResponse(RESPONSE.SERVER_ERROR)
        except Exception:
            return JsonResponse(RESPONSE.INVALID_REQUEST)
        return JsonResponse(RESPONSE.OPERATION_FAILED)

class ImageHandler(View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        try:
            if not request.FILES:
                return JsonResponse(RESPONSE.INVALID_REQUEST)
            f = request.FILES['file']
            tar_pattern = "[.](tar)$"
            searched_tar = re.search(tar_pattern, f.name, re.M|re.I)
            if searched_tar:
                try:
                    try:
                        image = client.images.load(f)[0]
                        name = image.tags[0]
                        newName = REGISTRY_ADDRESS + '/' + name
                        docker_api.tag(name, newName)
                        docker_api.push(newName)
                        return JsonResponse(RESPONSE.SUCCESS)
                    except docker.errors.DockerException as e:
                        return JsonResponse(RESPONSE.SERVER_ERROR)
                except Exception as e:
                    LOGGER.error(e)
        except Exception:
            return JsonResponse(RESPONSE.INVALID_REQUEST)
        return JsonResponse(RESPONSE.OPERATION_FAILED)
