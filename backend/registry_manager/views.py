import logging
import json
import urllib.error
import urllib.request
import urllib.parse
from django.http import JsonResponse
from django.views import View
from api.common import RESPONSE
from config import REGISTRY_V2_API_ADDRESS
from registry_manager.cache import cache_with_timeout
from registry_manager.manifest import makeManifest

LOGGER = logging.getLogger(__name__)

class ConnectionUtils:
    GET_ALL_REPOS_TEMPLATE = '{url}/_catalog'
    GET_MANIFEST_TEMPLATE = '{url}/{repo}/manifests/{tag}'
    GET_LAYER_TEMPLATE = '{url}/{repo}/blobs/{digest}'
    GET_ALL_TAGS_TEMPLATE = '{url}/{repo}/tags/list'

    POST_LAYER_TEMPLATE = '{url}/{repo}/blobs/uploads/'

    PUT_MANIFEST_TEMPLATE = '{url}/{repo}/manifests/{tag}'

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

    # get the size of a repository
    def get_size_of_repo(self, repo):
        result = 0

        for tag in self.get_tags(repo):
            result += self.get_size_of_layers(repo, tag)

        return result

    # get tag information
    def get_tag(self, repo, tag):
        try:
            tag_info = {}
            manifest = self.get_manifest(repo, tag)
            tag_info['Size'] = self.get_size_of_layers(repo, tag)
            tag_info['Layers'] = self.get_number_of_layers(repo, tag)
            tag_info['Created'] = manifest.get_created_date()
            tag_info['Entrypoint'] = manifest.get_entrypoint()
            tag_info['Docker Version'] = manifest.get_docker_version()
            tag_info['Exposed Ports'] = manifest.get_exposed_ports()
            tag_info['Volumes'] = manifest.get_volumes()
            return tag_info
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

    # get number of tags of a repository
    def get_number_of_tags(self, repo):
        return len(self.get_tags(repo))

    # get information of a repository
    def get_repository(self, repo):
        try:
            response = {}
            response['Number of Tags'] = self.get_number_of_tags(repo)
            response['Size of Repository'] = self.get_size_of_repo(repo)
            return response
        except Exception as ex:
            LOGGER.error(ex)

    # get repository list
    def get_repositories(self):
        try:
            repositories = self.json_request(
                self.GET_ALL_REPOS_TEMPLATE.format(
                    url=REGISTRY_V2_API_ADDRESS
                )
            )['repositories']
            return repositories
        except Exception as ex:
            LOGGER.error(ex)

    # urllib request
    def request_registry(self, *args, **kwargs):
        request = urllib.request.Request(*args, **kwargs)
        response = urllib.request.urlopen(request, timeout=5)
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
            for repository in self.util.get_repositories():
                response['payload'][repository] = self.util.get_repository(repository)
            return JsonResponse(response)
        except Exception as ex:
            LOGGER.error(ex)

class RepositoryHandler(View):
    http_method_names = ['get', 'post', 'put', 'delete']
    util = ConnectionUtils()

    def get(self, _, **kwargs):
        response = RESPONSE.SUCCESS
        try:
            for tag in self.util.get_tags(kwargs.get('repo')):
                response['payload'][tag] = self.util.get_tag(kwargs.get('repo'), tag)
            return JsonResponse(response)
        except Exception as ex:
            LOGGER.error(ex)

    # def post(self, request):
    #     query = json.loads(request.body)
