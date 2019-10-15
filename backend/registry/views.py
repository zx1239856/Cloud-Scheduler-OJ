"""View handlers for RegistryManager"""
import os
import re
import logging
import docker
from django.http import JsonResponse
from django.views import View

# Create your views here.
private_registry = "tcp://127.0.0.1:1234"
client = docker.from_env()
LOGGER = logging.getLogger(__name__)

class RegistryManagementHandler(View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        """
        @api {post} /image_registry/ post image.tar or Dockerfile
        @apiName PostImageToRegistry
        @apiGroup ImageRegistry
        @apiVersion 0.1.0
        @apiPermission admin
        """
        f = request.FILES['file']
        file_name = ""
        path = ""
        condition_code = 0

        tar_pattern = "[.](tar)$"
        dockerfile_pattern = "Dockerfile"
        searched_tar = re.search(tar_pattern, f.name, re.M|re.I)
        searched_dockerfile = re.search(dockerfile_pattern, f.name, re.M|re.I)
        if searched_tar:
            path = "registry/tars/"
            condition_code = 1
        elif searched_dockerfile:
            path = "registry/dockerfiles/"
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
                if condition_code == 1:
                    client.images.load(f)
                else:
                    client.images.build(path='registry/dockerfiles')
            except Exception as e:
                LOGGER.error(e)
            result = {
                'result': 'OK',
                'filename': request.FILES['file'].name,
            }
            return JsonResponse(result)


        return JsonResponse({'result': "didn't work"})
