import logging
import json
import re
import urllib.error
from urllib.request import Request
from urllib.request import urlopen
import urllib.parse
import docker
from django.http import JsonResponse
from django.views import View
from dxf import DXF
from dxf import DXFBase
from api.common import RESPONSE
from config import REGISTRY_V2_API_ADDRESS, DOCKER_ADDRESS, REGISTRY_ADDRESS
from registry_manager.cache import cache_with_timeout
from registry_manager.manifest import makeManifest

LOGGER = logging.getLogger(__name__)

class ConnectionUtils:
    client = docker.DockerClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)
    docker_api = docker.APIClient(base_url=DOCKER_ADDRESS, version='auto', tls=False)

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

    # get the size of a layer
    @cache_with_timeout()
    def get_size_of_layer(self, repo, layer_id):
        try:
            return int(
                self.request_registry(
                    self.GET_LAYER_TEMPLATE.format(
                        url=REGISTRY_V2_API_ADDRESS,
                        repo=repo,
                        digest=layer_id
                    ),
                    method='HEAD'
                ).info()['Content-Length']
            )
        except Exception as ex:
            LOGGER.error(ex)

    # get the amounts of layers in an image
    def get_number_of_layers(self, repo, tag):
        return len(self.get_layer_ids(repo, tag))

    # get layer ids in list
    def get_layer_ids(self, repo, tag):
        return self.get_manifest(repo, tag).get_layer_ids()

    # get size of all layers / image
    def get_size_of_layers(self, repo, tag):
        result = 0

        for image_id in self.get_layer_ids(repo, tag):
            result += self.get_size_of_layer(repo, image_id)

        return result

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
                tag_info['Docker Version'] = manifest.get_docker_version()
                tag_info['Exposed Ports'] = manifest.get_exposed_ports()
                tag_info['Volumes'] = manifest.get_volumes()
                tag_info['Size'] = self.get_size_of_layers(repo, tag)
                tag_info['Layers'] = self.get_number_of_layers(repo, tag)
                return tag_info
            else:
                return None
        except Exception as ex:
            LOGGER.error(ex)
            return None

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
            dxf = DXF(REGISTRY_ADDRESS, repo)
            images = []
            repo_size = 0

            for tag_name in dxf.list_aliases():
                image = self.get_tag(repo, tag_name)
                if image is not None:
                    images.append(image)
                    repo_size += image['Size']
            response = {
                'Repo': repo,
                'NumberOfTags': len(images),
                'SizeOfRepository': repo_size
            }
            return response
        except Exception as ex:
            LOGGER.error(ex)
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
    """
    get function for getting list of repositories with its info
    """
    def get(self, request):
        response = RESPONSE.SUCCESS
        try:
            response['payload']['entity'] = []
            dxfBase = DXFBase(REGISTRY_ADDRESS)
            for repository in dxfBase.list_repos():
                response['payload']['entity'].append(self.util.get_repository(repository))
            response['payload']['count'] = len(response['payload']['entity'])
            return JsonResponse(response)
        except Exception as ex:
            response = RESPONSE.OPERATION_FAILED
            response['payload']['error'] = str(ex)
            return JsonResponse(response)

class RepositoryHandler(View):
    http_method_names = ['get', 'post', 'put', 'delete']
    util = ConnectionUtils()

    def get(self, _, **kwargs):
        response = RESPONSE.SUCCESS
        try:
            response['payload']['entity'] = []
            for tag in self.util.get_tags(kwargs.get('repo')):
                image = self.util.get_tag(kwargs.get('repo'), tag)
                if image is not None:
                    response['payload']['entity'].append(image)
            response['payload']['count'] = len(response['payload']['entity'])
            return JsonResponse(response)
        except Exception as ex:
            response = RESPONSE.OPERATION_FAILED
            response['payload']['error'] = str(ex)
            return JsonResponse(response)

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
            files = request.FILES.getlist('file[]', None)
            if files is None:
                response = RESPONSE.INVALID_REQUEST
                response['message'] += " File is empty."
                return JsonResponse(response)
            for f in files:
                tar_pattern = "[.](tar)$"
                searched_tar = re.search(tar_pattern, f.name, re.M|re.I)
                if searched_tar:
                    try:
                        image = self.util.client.images.load(f)[0]
                        name = image.tags[0]
                        newName = REGISTRY_ADDRESS + '/' + name
                        self.util.docker_api.tag(name, newName)
                        self.util.docker_api.push(newName)
                    except docker.errors.DockerException as e:
                        response = RESPONSE.SERVER_ERROR
                        response['payload']['docker exception'] = str(e)
                        return JsonResponse(response)
            return JsonResponse(RESPONSE.SUCCESS)
        except Exception as e:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += str(e)
            return JsonResponse(response)
        return JsonResponse(RESPONSE.NOT_IMPLEMENTED)

    def delete(self, request, **kwargs):
        try:
            repo = kwargs.get('repo')
            tag = kwargs.get('tag')
            dxf = DXF(REGISTRY_ADDRESS, repo)
            digest = dxf.get_digest(tag)
            try:
                dxf.del_blob(digest)
            except urllib.error.HTTPError as ex:
                response = RESPONSE.SERVER_ERROR
                response['payload']['error'] = str(ex)
                return JsonResponse(response)
            return JsonResponse(RESPONSE.SUCCESS)
        except Exception as ex:
            response = RESPONSE.OPERATION_FAILED
            response['payload']['error'] = str(ex)
            return JsonResponse(response)
