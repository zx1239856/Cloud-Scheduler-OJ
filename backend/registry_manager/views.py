import logging
import json
import re
import os
from threading import Thread
from urllib.request import Request
from urllib.request import urlopen
from docker import DockerClient, APIClient
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from dxf import DXF
from dxf import DXFBase
from api.common import RESPONSE
from config import REGISTRY_V2_API_ADDRESS, DOCKER_ADDRESS, REGISTRY_ADDRESS
from registry_manager.manifest import makeManifest
from user_model.views import permission_required

LOGGER = logging.getLogger(__name__)

class ConnectionUtils:
    GET_MANIFEST_TEMPLATE = '{url}/{repo}/manifests/{tag}'
    GET_LAYER_TEMPLATE = '{url}/{repo}/blobs/{digest}'
    GET_ALL_TAGS_TEMPLATE = '{url}/{repo}/tags/list'

    # get the manifest of a specific tagged image
    def get_manifest(self, repo, tag):
        try:
            manifest = makeManifest(
                self.json_request(
                    self.GET_MANIFEST_TEMPLATE.format(
                        url=REGISTRY_V2_API_ADDRESS,
                        repo=repo,
                        tag=tag
                    )
                )
            )
            return manifest
        except Exception as ex:
            LOGGER.error(ex)

    # get tag information
    def get_tag(self, repo, tag):
        try:
            tag_info = {}
            dxf = DXF(REGISTRY_ADDRESS, repo)
            digest = dxf.get_digest(tag)
            response = self.request_registry(
                self.GET_LAYER_TEMPLATE.format(
                    url=REGISTRY_V2_API_ADDRESS,
                    repo=repo,
                    digest=digest
                ),
                method='HEAD'
            )
            if response.status == 200:
                manifest = self.get_manifest(repo, tag)
                tag_info['Tag'] = tag
                tag_info['Created'] = manifest.get_created_date()
                tag_info['Entrypoint'] = manifest.get_entrypoint()
                tag_info['DockerVersion'] = manifest.get_docker_version()
                tag_info['ExposedPorts'] = manifest.get_exposed_ports()
                tag_info['Volumes'] = manifest.get_volumes()
                return tag_info
            else:
                return None
        except Exception as ex:
            LOGGER.error(ex)

    # get tags of a repository in list
    def get_tags(self, repo):
        try:
            tags = self.json_request(
                self.GET_ALL_TAGS_TEMPLATE.format(
                    url=REGISTRY_V2_API_ADDRESS,
                    repo=repo
                )
            )['tags']
            return tags
        except Exception as ex:
            LOGGER.error(ex)

    # get information of a repository
    def get_repository(self, repo):
        try:
            response = {
                'Repo': repo,
            }
            return response
        except Exception as ex:
            return str(ex)

    # urllib request
    def request_registry(self, *args, **kwargs):
        request = Request(*args, **kwargs)
        response = urlopen(request, timeout=5)
        return response

    # decoder of json request
    def string_request(self, *args, **kwargs):
        response = self.request_registry(*args, **kwargs).read().decode()
        return response

    # json format request
    def json_request(self, *args, **kwargs):
        response = self.string_request(*args, **kwargs)
        return json.loads(response)


class RegistryHandler(View):
    http_method_names = ['get']
    util = ConnectionUtils()

    @method_decorator(permission_required)
    def get(self, request, **_):
        """
        @api {get} /registry/ Get Repository list
        @apiName GetRepositories
        @apiGroup RegistryManager
        @apiVersion 0.1.0
        @apiPermission admin
        @apiSuccess {Object} payload Response Object
        @apiSuccess {Number} payload.count Count of total repositories
        @apiSuccess {Object[]} payload.entry List of Repositoris
        @apiSuccess {String} payload.entry.Repo Repository Name
        @apiSuccess {String} payload.entry.NumberOfTags Number of Tags
        @apiSuccess {String} payload.entry.SizeOfRepository Size of Repository
        @apiUse APIHeader
        @apiUse Success
        @apiUse OperationFailed
        @apiUse Unauthorized
        """
        response = RESPONSE.SUCCESS
        try:
            response['payload']['entity'] = []
            dxfBase = DXFBase(REGISTRY_ADDRESS)
            for repository in dxfBase.list_repos():
                response['payload']['entity'].append(self.util.get_repository(repository))
            response['payload']['count'] = len(response['payload']['entity'])
            return JsonResponse(response)
        except Exception:
            return JsonResponse(RESPONSE.OPERATION_FAILED)


class RepositoryHandler(View):
    http_method_names = ['get', 'post', 'put', 'delete']
    util = ConnectionUtils()
    basePath = 'registry_manager/data/'

    @method_decorator(permission_required)
    def get(self, _, **kwargs):
        """
        @api {get} registry/<str:repo>/ Get Tag Lists of the given Repository
        @apiName GetTags
        @apiGroup RegistryManager
        @apiVersion 0.1.0
        @apiPermission admin
        @apiSuccess {Object} payload Response Object
        @apiSuccess {Number} payload.count Count of total Tags
        @apiSuccess {Object[]} payload.entry List of Tags
        @apiSuccess {String} payload.entry.Tag Tag Name
        @apiSuccess {String} payload.entry.Created Tag Created Time
        @apiSuccess {String} payload.entry.Entrypoint Entrypoint of the Tag
        @apiSuccess {String} payload.entry.DockerVersion Docker Version of the Tag
        @apiSuccess {String} payload.entry.ExposedPorts Exposed Ports of the Tag
        @apiSuccess {String} payload.entry.Volumes Volumes of the Tag
        @apiSuccess {String} payload.entry.Size Size of the Tag
        @apiSuccess {String} payload.entry.Layers Number of Layers of the Tag
        @apiUse APIHeader
        @apiUse Success
        @apiUse OperationFailed
        @apiUse Unauthorized
        """
        response = RESPONSE.SUCCESS
        try:
            response['payload']['entity'] = []
            for tag in self.util.get_tags(kwargs.get('repo')):
                image = self.util.get_tag(kwargs.get('repo'), tag)
                if image is not None:
                    response['payload']['entity'].append(image)
            response['payload']['count'] = len(response['payload']['entity'])
            return JsonResponse(response)
        except Exception:
            return JsonResponse(RESPONSE.OPERATION_FAILED)

    @method_decorator(permission_required)
    def post(self, request, **_):
        """
        @api {post} /registry/upload/ Upload image.tar
        @apiName UploadImageTar
        @apiGroup RegistryManager
        @apiVersion 0.1.0
        @apiPermission admin
        @apiParamExample {json} Request-Example:
        {
            "file": [FILE]
        }
        @apiParam {Object} The image.tar file to be uploaded
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        """
        try:
            files = request.FILES.getlist('file[]', None)
            if not files:
                response = RESPONSE.INVALID_REQUEST
                response['message'] += " File is empty."
                return JsonResponse(response)
            for f in files:
                tar_pattern = "[.](tar)$"
                searched_tar = re.search(tar_pattern, f.name, re.M|re.I)
                if searched_tar:
                    self.cacheFile(f)
            return JsonResponse(RESPONSE.SUCCESS)
        except Exception:
            return JsonResponse(RESPONSE.OPERATION_FAILED)

    def cacheFile(self, file):
        if not os.path.exists(self.basePath):
            os.makedirs(self.basePath)
        writeFile = open(self.basePath + file.name, 'wb+')
        for chunk in file.chunks():
            writeFile.write(chunk)
        writeFile.close()
        print(file.name)
        upload = Thread(target=self.upload, args=(file.name,))
        upload.start()

    def upload(self, filename):
        client = DockerClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)
        docker_api = APIClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)
        readFile = open(self.basePath+filename, 'rb+')
        file = readFile.read()
        image = client.images.load(file)[0]
        name = image.tags[0]
        newName = REGISTRY_ADDRESS + '/' + name
        docker_api.tag(name, newName)
        docker_api.push(newName)
        readFile.close()
        if os.path.exists(self.basePath + filename):
            os.remove(self.basePath + filename)

    @method_decorator(permission_required)
    def delete(self, request, **kwargs):
        """
        @api {delete} /registry/<str:repo>/<str:tag>/ Delete an image
        @apiName DeleteImage
        @apiGroup RegistryManager
        @apiVersion 0.1.0
        @apiPermission admin
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse OperationFailed
        @apiUse Unauthorized
        """
        try:
            repo = kwargs.get('repo')
            tag = kwargs.get('tag')
            dxf = DXF(REGISTRY_ADDRESS, repo)
            digest = dxf.get_digest(tag)
            dxf.del_blob(digest)
            return JsonResponse(RESPONSE.SUCCESS)
        except Exception:
            return JsonResponse(RESPONSE.OPERATION_FAILED)
