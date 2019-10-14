from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm
import docker
import json
import os
import time
import re
import logging

# Create your views here.
private_registry = "tcp://127.0.0.1:1234"
client = docker.from_env()
LOGGER = logging.getLogger(__name__)

def load_tar(f):
    image = client.images.load(f)
    # print(image)

def build_dockerfile():
    client.images.build(path='registry/dockerfiles')

def handle_uploaded_file(f):
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

    if condition_code == 1 or condition_code == 2:
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            file_name = path + f.name
            destination = open(file_name, 'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            if condition_code == 1:
                load_tar(f)
            else:
                build_dockerfile()
        except Exception as e:
            LOGGER.error(e)

    return file_name


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        # if form.is_valid():
        handle_uploaded_file(request.FILES['file'])
        result = {
            'result': 'OK',
            'filename': request.FILES['file'].name,
        }
        return HttpResponse(json.dumps(result))
    else:
        form = UploadFileForm()
    return HttpResponse(json.dumps({'result': "didn't work"}))
