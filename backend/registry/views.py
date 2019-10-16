"""View handlers for RegistryManager"""
import os
import re
import logging
import requests
import docker
from django.http import JsonResponse
from django.views import View

# Create your views here.
private_registry = "tcp://127.0.0.1:1234"
client = docker.from_env()
path = "registry/data/"
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
        result = {
            'condition': '',
            'filename': request.FILES['file'].name,
            'error': '',
        }
        try:
            if not request.FILES:
                return JsonResponse({'error': "File is empty!"})
            f = request.FILES['file']
            file_name = ""
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
                        client.images.build(path='registry/data')
                    except docker.errors.DockerException as e:
                        result['error'] = 'Dockerfile build error' + e.__context__
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
        result = {
            'condition': '',
            'filename': request.FILES['file'].name,
            'error': '',
        }
        try:
            if not request.FILES:
                return JsonResponse({'error': "File is empty!"})
            f = request.FILES['file']
            tar_pattern = "[.](tar)$"
            searched_tar = re.search(tar_pattern, f.name, re.M|re.I)
            if searched_tar:
                try:
                    try:
                        client.images.load(f)
                    except docker.errors.DockerException as e:
                        result['error'] = 'Dockerfile build error' + e.__context__
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
