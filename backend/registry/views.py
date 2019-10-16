"""View handlers for RegistryManager"""
import os
import re
import logging
import requests
import docker
from django.http import JsonResponse
from django.views import View
from config import DOCKER_ADDRESS, REGISTRY_ADDRESS

client = docker.DockerClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)
docker_api = docker.APIClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)
LOGGER = logging.getLogger(__name__)

def test_docker_is_running():
    try:
        client.ping()
        return True
    except (requests.exceptions.ConnectionError, docker.errors.APIError):
        return False

class DockerfileHandler(View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        # print(test_docker_is_running())
        result = {
            'condition': '',
            'filename': request.FILES['file'].name,
            'error': '',
        }
        try:
            if len(request.FILES) == 0:
                return JsonResponse({'error': "File is empty!"})
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
                    try:
                        image = client.images.build(path='registry/data')[0]
                        name = image.tags[0]
                        newName = REGISTRY_ADDRESS + '/' + name
                        docker_api.tag(name, newName)
                        docker_api.push(newName)
                        # client.images.push(repository=REGISTRY_ADDRESS + '/' + f.name)
                    except docker.errors.DockerException as e:
                        result['error'] = 'Dockerfile build error ' + str(e.__context__)
                        return JsonResponse(result)
                    result['condition'] = 'OK'
                except Exception as e:
                    LOGGER.error(e)
            else:
                result['condition'] = 'Not OK'
                result['error'] = "there is no file called 'Dockerfile'"
            return JsonResponse(result)
        except Exception:
            result['error'] = 'error with file'
        finally:
            return JsonResponse(result)
        return JsonResponse(result)

class ImageHandler(View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        # print(test_docker_is_running())
        result = {
            'condition': '',
            'filename': request.FILES['file'].name,
            'error': '',
        }
        try:
            if len(request.FILES) == 0:
                return JsonResponse({'error': "File is empty!"})
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
                    except docker.errors.DockerException as e:
                        result['error'] = 'Image load error: ' + str(e)
                        return JsonResponse(result)
                    result['condition'] = 'OK'
                except Exception as e:
                    LOGGER.error(e)
            else:
                result['condition'] = 'Not OK'
                result['error'] = "there is no file called 'Dockerfile'"
            return JsonResponse(result)
        except Exception:
            result['error'] = 'error with file'
        finally:
            return JsonResponse(result)
