import abc
import base64
import json
import logging
import urllib.error
import urllib.request
import urllib.parse
from backend.registry_manager.cache import CacheWithTimeout
from backend.registry_manager.manifest import makeManifest

LOGGER = logging.getLogger(__name__)


class DockerRegistry(abc.ABC):

    @property
    def supports_repo_deletion(self):
        return False

    def json_request(self, *args, **kwargs):
        return json.loads(
            self.string_request(*args, **kwargs)
        )

    @CacheWithTimeout(1)  # enable caching to improve performance of multiple consecutive calls
    def string_request(self, *args, **kwargs):
        return self.request(*args, **kwargs).read().decode()

    def request(self, *args, **kwargs):
        request = urllib.request.Request(*args, **kwargs)

        if self._user and self._password:
            base64string = base64.b64encode(
                f'{self._user}:{self._password}'.encode()
            ).decode('ascii')
            request.add_header("Authorization", f"Basic {base64string}")

        return urllib.request.urlopen(request, timeout=3)

    # def delete_repo(self, repo):
    #     raise NotImplementedError

    def get_number_of_repos(self):
        return len(self.get_repos())

    def get_number_of_tags(self, repo):
        return len(self.get_tags(repo))

    def get_number_of_layers(self, repo, tag):
        return len(self.get_layer_ids(repo, tag))

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


class DockerV2Registry(DockerRegistry):
    API_BASE = '{url}/v2/'
    GET_ALL_REPOS_TEMPLATE = '{url}/v2/_catalog'
    GET_ALL_TAGS_TEMPLATE = '{url}/v2/{repo}/tags/list'
    GET_MANIFEST_TEMPLATE = '{url}/v2/{repo}/manifests/{tag}'
    GET_LAYER_TEMPLATE = '{url}/v2/{repo}/blobs/{digest}'

    version = 2

    def __init__(self, name, url, user=None, password=None):
        self._name = name
        self._url = url if url.startswith('http') else 'http://' + url
        self._user = user
        self._password = password

    def __key(self):
        return self._url

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    # @property
    # def supports_tag_deletion(self):
    #     try:
    #         self.request(
    #             DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
    #                 url=self._url,
    #                 repo='foo',
    #                 tag='bar'
    #             ),
    #             method='DELETE'
    #         )
    #     except urllib.error.HTTPError as e:
    #         if e.code == 405:
    #             return False
    #         else:
    #             return True

    def delete_tag(self, repo, tag):
        digest = self.request(
            DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                url=self._url,
                repo=repo,
                tag=tag
            ),
            method='HEAD',
            headers={'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
        ).info()['Docker-Content-Digest']

        try:
            self.request(
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo=repo,
                    tag=digest
                ),
                method='DELETE'
            )
        except urllib.error.HTTPError:
            raise ConnectionError

    @CacheWithTimeout()
    def get_manifest(self, repo, tag):
        return makeManifest(
            self.json_request(
                DockerV2Registry.GET_MANIFEST_TEMPLATE.format(
                    url=self._url,
                    repo=repo,
                    tag=tag
                )
            )
        )

    # def is_online(self):
    #     try:
    #         resp = self.request(
    #             DockerV2Registry.API_BASE.format(
    #                 url=self._url
    #             )
    #         )
    #     except (urllib.error.URLError, socket.timeout):
    #         return False

    #     return True if resp.getcode() == 200 else False

    def get_repos(self):
        return self.json_request(
            DockerV2Registry.GET_ALL_REPOS_TEMPLATE.format(
                url=self._url
            )
        )['repositories']

    def get_tags(self, repo):
        tags = self.json_request(
            DockerV2Registry.GET_ALL_TAGS_TEMPLATE.format(
                url=self._url,
                repo=repo
            )
        )['tags']

        return tags or []

    def get_layer_ids(self, repo, tag):
        return self.get_manifest(repo, tag).get_layer_ids()

    @CacheWithTimeout()
    def get_size_of_layer(self, repo, layer_id):
        try:
            return int(
                self.request(
                    DockerV2Registry.GET_LAYER_TEMPLATE.format(
                        url=self._url,
                        repo=repo,
                        digest=layer_id
                    ),
                    method='HEAD'
                ).info()['Content-Length'])

        except urllib.error.HTTPError:  # required to support Windows images, see https://github.com/brennerm/docker-registry-frontend/issues/5
            return 0

    def get_created_date(self, repo, tag):
        return self.get_manifest(repo, tag).get_created_date()

    def get_entrypoint(self, repo, tag):
        return self.get_manifest(repo, tag).get_entrypoint()

    def get_docker_version(self, repo, tag):
        return self.get_manifest(repo, tag).get_docker_version()

    def get_exposed_ports(self, repo, tag):
        return self.get_manifest(repo, tag).get_exposed_ports()

    def get_volumes(self, repo, tag):
        return self.get_manifest(repo, tag).get_volumes()


def make_registry(*args, **kwargs):
    v2registry = DockerV2Registry(*args, **kwargs)

    if v2registry.is_online():
        return v2registry
    else:
        return v2registry
