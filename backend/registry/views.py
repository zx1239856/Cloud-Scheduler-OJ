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
LOGGER = logging.getLogger(__name__)

class RegistryManagementHandler(View):
    http_method_names = ['post']

    def test_docker_is_running(self):
        try:
            client.ping()
            return True
        except (requests.exceptions.ConnectionError, docker.errors.APIError):
            return False

    def post(self, request, **kwargs):
        """
        @api {post} /image_registry/ post image.tar or Dockerfile
        @apiName PostImageToRegistry
        @apiGroup ImageRegistry
        @apiVersion 0.1.0
        @apiPermission admin
        """
        try:
            if len(request.FILES) == 0:
                return JsonResponse({'result': "File is empty!"})
            f = request.FILES['file']
            file_name = ""
            path = "registry/data/"
            condition_code = 0

            tar_pattern = "[.](tar)$"
            dockerfile_pattern = "Dockerfile"
            searched_tar = re.search(tar_pattern, f.name, re.M|re.I)
            searched_dockerfile = re.search(dockerfile_pattern, f.name, re.M|re.I)
            if searched_tar:
                condition_code = 1
            elif searched_dockerfile:
                condition_code = 2

            if condition_code in (1, 2):
                try:
                    if not os.path.exists(path):
                        os.makedirs(path)
                    file_name = path + f.name
                    destination = open(file_name, 'wb+')
                    for chunk in f.chunks():
                        destination.write(chunk)
                    destination.close()
                    try:
                        if condition_code == 1:
                            client.images.load(f)
                        else:
                            client.images.build(path='registry/data')
                    except docker.errors.DockerException:
                        return JsonResponse({'docker error': 'build error'})
                except Exception as e:
                    LOGGER.error(e)
                result = {
                    'result': 'OK',
                    'filename': request.FILES['file'].name,
                }
                return JsonResponse(result)
        except Exception as ex:
            LOGGER.error(ex)
            raise


        return JsonResponse({'result': "didn't work"})
