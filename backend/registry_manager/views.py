import logging
import json
import re
import os
import hashlib
import time
from threading import Thread
from urllib.request import Request
from urllib.request import urlopen
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from dxf import DXF
from dxf import DXFBase
from api.common import RESPONSE
from config import REGISTRY_V2_API_ADDRESS, REGISTRY_ADDRESS
from registry_manager.manifest import make_manifest
from registry_manager.models import ImageModel, ImageStatusCode
from registry_manager.uploader import DockerTarUploader
from user_model.views import permission_required

LOGGER = logging.getLogger(__name__)


class ConnectionUtils:
    GET_MANIFEST_TEMPLATE = '{url}/{repo}/manifests/{tag}'
    GET_LAYER_TEMPLATE = '{url}/{repo}/blobs/{digest}'
    GET_ALL_TAGS_TEMPLATE = '{url}/{repo}/tags/list'

    # get the manifest of a specific tagged image
    def get_manifest(self, repo, tag):
        try:
            manifest = make_manifest(
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
        response = {
            'Repo': repo,
        }
        return response

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
    def get(self, _req, **_):
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
        @apiUse APIHeader
        @apiUse Success
        @apiUse OperationFailed
        @apiUse Unauthorized
        """
        response = RESPONSE.SUCCESS
        try:
            response['payload']['entity'] = []
            dxfbase = DXFBase(REGISTRY_ADDRESS)
            for repository in dxfbase.list_repos():
                response['payload']['entity'].append(self.util.get_repository(repository))
            response['payload']['count'] = len(response['payload']['entity'])
            return JsonResponse(response)
        except Exception as ex:
            LOGGER.exception(ex)
            return JsonResponse(RESPONSE.OPERATION_FAILED)


class RepositoryHandler(View):
    http_method_names = ['get', 'post', 'put', 'delete']
    util = ConnectionUtils()
    basePath = 'registry_manager/data/'

    @method_decorator(permission_required)
    def get(self, _, **kwargs):
        """
        @api {get} registry/repository/<str:repo>/ Get Tag Lists of the given Repository
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
        except Exception as ex:
            LOGGER.exception(ex)
            return JsonResponse(RESPONSE.OPERATION_FAILED)

    @method_decorator(permission_required)
    def post(self, request, **_):
        """
        @api {post} /registry/repository/upload/ Upload image.tar
        @apiName UploadImageTar
        @apiGroup RegistryManager
        @apiVersion 0.1.0
        @apiPermission admin
        @apiParamExample {json} Request-Example:
        {
            "file": [FILE]，
            "repo": ''
        }
        @apiParam {Object} The image.tar file to be uploaded
        @apiParam {String} The Repository name
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
            repo = request.POST.get('repo', None)
            if not files:
                response = RESPONSE.INVALID_REQUEST
                response['message'] += " File is empty."
                return JsonResponse(response)
            for f in files:
                tar_pattern = "[.](tar)$"
                searched_tar = re.search(tar_pattern, f.name, re.M | re.I)
                if searched_tar:
                    upload_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    md = hashlib.md5()
                    md.update((f.name + upload_time).encode('utf-8'))
                    md = md.hexdigest()
                    file_model = ImageModel(hashid=md, filename=f.name, status=ImageStatusCode.PENDING,
                                            uploadtime=upload_time)
                    file_model.save()
                    ImageModel.objects.filter(hashid=md).update(status=ImageStatusCode.CACHING)
                    self.cacheFile(f, md, repo)
            return JsonResponse(RESPONSE.SUCCESS)
        except Exception as ex:
            LOGGER.exception(ex)
            return JsonResponse(RESPONSE.OPERATION_FAILED)

    def cacheFile(self, file, md, repo):
        if not os.path.exists(self.basePath):
            os.makedirs(self.basePath)
        writefile = open(self.basePath + file.name, 'wb+')
        for chunk in file.chunks():
            writefile.write(chunk)
        writefile.close()
        ImageModel.objects.filter(hashid=md).update(status=ImageStatusCode.CACHED)
        upload = Thread(target=self.upload, args=(file.name, md, repo))
        upload.start()

    def upload(self, filename, md, repo):
        try:
            ImageModel.objects.filter(hashid=md).update(status=ImageStatusCode.UPLOADING)
            dxf = DXF(REGISTRY_ADDRESS, repo)
            status = DockerTarUploader(dxf).upload_tar(self.basePath + filename)
            LOGGER.info("upload status")
            LOGGER.info(status)
            if os.path.exists(self.basePath + filename):
                os.remove(self.basePath + filename)
            LOGGER.info("done upload")
            ImageModel.objects.filter(hashid=md).update(status=ImageStatusCode.SUCCEEDED)
        except Exception as ex:
            LOGGER.exception(ex)
            ImageModel.objects.filter(hashid=md).update(status=ImageStatusCode.FAILED)

    @method_decorator(permission_required)
    def delete(self, _, **kwargs):
        """
        @api {delete} /registry/repository/<str:repo>/<str:tag>/ Delete an image
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
        except Exception as ex:
            LOGGER.exception(ex)
            return JsonResponse(RESPONSE.OPERATION_FAILED)


class UploadHandler(View):
    http_method_names = ['get']

    @method_decorator(permission_required)
    def get(self, request, **_):
        """
        @api {get} /registry/history/ Get uploading image list
        @apiName getImageList
        @apiGroup RegistryManager
        @apiVersion 0.1.0
        @apiPermission admin
        @apiSuccess {Object} payload Response Object
        @apiSuccess {Number} payload.count Count of total images
        @apiSuccess {Number} payload.page_count Count of total pages
        @apiSuccess {Object[]} payload.entry List of images
        @apiSuccess {String} payload.entry.name Filename
        @apiSuccess {Number} payload.entry.status File uploading status
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """
        try:
            page = int(request.GET.get('page', 1))
            image_list = ImageModel.objects.all().order_by('-uploadtime')
            response = RESPONSE.SUCCESS
            payload = {
                'count': len(image_list),
                'page_count': (len(image_list) + 24) // 25,
                'entry': []
            }
            if (page < 1 or page > payload['page_count']) and (page != 1 or payload['page_count'] != 0):
                raise ValueError()
            for f in image_list[25 * (page - 1): 25 * page]:
                payload['entry'].append({'id': f.hashid,
                                         'name': f.filename,
                                         'status': f.status,
                                         'time': f.uploadtime,
                                         })
            response['payload'] = payload
            return JsonResponse(response)
        except Exception as ex:
            LOGGER.exception(ex)
            return JsonResponse(RESPONSE.INVALID_REQUEST)
