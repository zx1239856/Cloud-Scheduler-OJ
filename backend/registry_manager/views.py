import logging
import json
import urllib.error
import urllib.request
import urllib.parse
from django.http import JsonResponse
from django.views import View
from api.common import RESPONSE
from config import REGISTRY_V2_API_ADDRESS
from backend.registry_manager.cache import cache_with_timeout
from backend.registry_manager.manifest import makeManifest

LOGGER = logging.getLogger(__name__)

class ConnectionUtils:


    def request_registry(self, *args, **kwargs):
        request = urllib.request.Request(*args, **kwargs)
        response = urllib.request.urlopen(request, timeout=5)
        return response

    def string_request(self, *args, **kwargs):
        response = self.request_registry(*args, **kwargs).read().decode()
        return response

    def json_request(self, *args, **kwargs):
        response = self.string_request(*args, **kwargs)
        return json.loads(response)

    def get_tags(self, repo):
        try:
            response = RESPONSE.SUCCESS
            response['payload'] = self.json_request(
                self.GET_ALL_TAGS_TEMPLATE.format(
                    url=REGISTRY_V2_API_ADDRESS,
                    repo=repo
                )
            )['tags']

            return JsonResponse(response)
        except Exception as ex:
            LOGGER.error(ex)

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

    def get_number_of_layers(self, repo, tag):
        return len(self.get_layer_ids(repo, tag))

    def get_layer_ids(self, repo, tag):
        return self.get_manifest(repo, tag).get_layer_ids()

    def get_size_of_layers(self, repo, tag):
        result = 0

        for image_id in self.get_layer_ids(repo, tag):
            result += self.get_size_of_layer(repo, image_id)

        return result

    def get_size_of_repo(self, repo):
        result = 0

        for tag in self.get_tags(repo):
            result += self.get_size_of_layers(repo, tag)

        return result

class RegistryHandler(View):
    http_method_names = ['get']
    GET_ALL_REPOS_TEMPLATE = '{url}/_catalog'
    util = ConnectionUtils()


    """
    get function for getting list of images
    """
    def get(self, request):
        try:
            response = RESPONSE.SUCCESS
            response['payload'] = self.util.json_request(
                self.GET_ALL_REPOS_TEMPLATE.format(
                    url=REGISTRY_V2_API_ADDRESS
                )
            )['repositories']
            return JsonResponse(response)
        except Exception as ex:
            LOGGER.error(ex)

class TagHandler(View):
    http_method_name = ['get']
    util = ConnectionUtils()

    GET_ALL_TAGS_TEMPLATE = '{url}/{repo}/tags/list'

    def get(self, _, **kwargs):
        try:
            response = RESPONSE.SUCCESS
            response['payload'] = self.util.json_request(
                self.GET_ALL_TAGS_TEMPLATE.format(
                    url=REGISTRY_V2_API_ADDRESS,
                    repo=kwargs.get('repo', None)
                )
            )['tags']

            return JsonResponse(response)
        except Exception as ex:
            LOGGER.error(ex)

class RepositoryHandler(View):
    http_method_names = ['get', 'post', 'put', 'delete']
    util = ConnectionUtils()

    GET_MANIFEST_TEMPLATE = '{url}/{repo}/manifests/{tags}'
    GET_LAYER_TEMPLATE = '{url}/{repo}/blobs/{digest}'
    POST_LAYER_TEMPLATE = '{url}/{repo}/blobs/uploads/'
    PUT_MANIFEST_TEMPLATE = '{url}/{repo}/manifests/{tags}'
    GET_ALL_TAGS_TEMPLATE = '{url}/{repo}/tags/list'

    def get(self, _, **kwargs):
        try:
            response = RESPONSE.SUCCESS
            manifest = self.util.get_manifest(kwargs.get('repo'), kwargs.get('tag'))
            response['payload']['created data'] = manifest.get_created_data()
            response['payload']['entry point'] = manifest.get_entrypoint()
            response['payload']['docker version'] = manifest.get_docker_version()
            response['payload']['exposed ports'] = manifest.get_exposed_ports()
            response['payload']['volumes'] = manifest.get_volumes()
            response['payload']['repo size'] = self.util.get_size_of_repo(kwargs.get('repo'))
            return JsonResponse(response)
        except Exception as ex:
            LOGGER.error(ex)

    def post(self, request):
        try:
            query = json.loads(request.body)
            response = self.util.json_request(
                self.POST_LAYER_TEMPLATE.format(
                    url=REGISTRY_V2_API_ADDRESS,
                    repo=str(query['repo'])
                ),
                method='POST'
            )
            return JsonResponse(response)
        except Exception as ex:
            LOGGER.error(ex)
