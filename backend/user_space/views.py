"""
View handler for user_space
"""

import logging
import json
import random
import string
from django.http import JsonResponse
from django.views import View
from kubernetes.client import CoreV1Api
from kubernetes.stream import stream
from kubernetes.stream.ws_client import ERROR_CHANNEL
from api.common import RESPONSE
from task_manager.executor import TaskExecutor, get_kubernetes_api_client
from task_manager.models import TaskSettings
from config import KUBERNETES_NAMESPACE

LOGGER = logging.getLogger(__name__)


def random_string():
    return ''.join(random.sample(string.ascii_letters + string.digits, 16))


class UserSpaceHandler(View):
    http_method_names = ['get', 'post', 'put', 'delete']

    def _get_pod(self, **kwargs):
        """
        :param kwargs: parameters needed
        :return: pod: the pod allocated; username: the username to execute file ops
        """
        user = kwargs.get('__user', None)
        if user is None:
            raise Exception("Internal exception raised when trying to get `User` object.")
        settings_uuid = kwargs.get('uuid', None)
        if settings_uuid is None:
            raise ValueError
        settings = TaskSettings.objects.get(uuid=settings_uuid)
        username = '{}_{}'.format(user.username, settings.id)
        executor = TaskExecutor.instance(new=False)
        if executor is None:
            return None, username
        else:
            pod = executor.get_user_space_pod(settings_uuid, user)
            return pod, username

    def _safe_wrapper(self, request, op_code, **kwargs):
        response = None
        api = CoreV1Api(get_kubernetes_api_client())
        try:
            pod, username = self._get_pod(**kwargs)
            if pod is None:
                response = RESPONSE.OPERATION_FAILED
                response['message'] += " Failed to allocate pod."
            else:
                params = request.GET
                command = ['su', username, '-c']
                cmdlist = []
                file = params.get('file', None)
                path = params.get('path', None)
                base64 = params.get('base64', None)
                if op_code != 'get':
                    query = json.loads(request.body)
                    file = query.get('file', None)
                    path = query.get('path', None)
                    content = query.get('content', '')
                if op_code == 'put':
                    old_file = query.get('old_file', None)
                    old_path = query.get('old_path', None)
                if not bool(file) ^ bool(path):
                    response = RESPONSE.INVALID_REQUEST
                else:
                    if op_code == 'put' and not ((old_file and file and not path) or (old_path and path and not file
                                                                                      and not content)):
                        response = RESPONSE.INVALID_REQUEST
                    else:
                        if file is not None:
                            if op_code == 'get':
                                cmdlist.append(('cat {}' if not base64 else 'base64 {}').format(file))
                            elif op_code == 'post':
                                delimiter = random_string()
                                cmdlist.append(
                                    "head -c -1 > {file} <<'{closing}'\n{content}\n{closing}".format(file=file,
                                                                                                     content=content,
                                                                                                     closing=delimiter))
                            elif op_code == 'delete':
                                cmdlist.append('rm -f {}'.format(file))
                        elif path is not None:
                            if op_code == 'get':
                                cmdlist.append('ls -F {}'.format(path))
                            elif op_code == 'post':
                                cmdlist.append('mkdir -p {}'.format(path))
                            elif op_code == 'delete':
                                cmdlist.append('rm -rf {}'.format(path))
                        if op_code == 'put':
                            if old_file and old_file != file:
                                cmdlist.append('mv {} {}'.format(old_file, file))
                            elif old_path and old_path != path:
                                cmdlist.append('mv {} {}'.format(old_path, path))
                            if file and content:
                                delimiter = random_string()
                                cmdlist.append(
                                    "head -c -1 > {file} <<'{closing}'\n{content}\n{closing}".format(file=file,
                                                                                                     content=content,
                                                                                                     closing=delimiter))
                        command.append(';'.join(cmdlist))
                        LOGGER.debug(command)
                        client = stream(api.connect_get_namespaced_pod_exec,
                                        pod.metadata.name, KUBERNETES_NAMESPACE, command=command, stderr=True,
                                        stdin=False,
                                        stdout=True, tty=False, _preload_content=False)
                        client.run_forever(timeout=20)
                        try:
                            err = json.loads(client.read_channel(ERROR_CHANNEL))
                        except ValueError:
                            err = {}
                        res = client.read_stdout()
                        LOGGER.debug(res)
                        LOGGER.debug(err)
                        if err['status'] == 'Success':
                            response = RESPONSE.SUCCESS
                            if op_code == 'get':
                                response['payload'] = res.split() if path is not None else res
                        else:
                            response = RESPONSE.OPERATION_FAILED
                return response
        except TaskSettings.DoesNotExist:
            response = RESPONSE.OPERATION_FAILED
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            response = RESPONSE.SERVER_ERROR
            LOGGER.error(ex)
        finally:
            return JsonResponse(response)

    def get(self, request, **kwargs):
        """
        @api {get} /user_space/<str:uuid>/ Get file/directory in user space
        @apiDescription Get the content of a file, or list a dir in user space. `file` and `path` parameter may not
        be used together. If the user enters user space for the first time, the content in `initial` folder of the
        task will be copied.
        @apiName GetItemUserSpace
        @apiGroup UserSpace
        @apiVersion 0.1.0
        @apiPermission user

        @apiParam {String} [file] Filename
        @apiParam {String} [path] Path
        @apiParam {Boolean} [base64] Return base64 encoded binary contents
        @apiSuccess {Object} payload Response payload. Can either be string of file content (when `file` is present)
        or list of file and path names (when `path` is present). The path name is followed by a trailing slash.
        @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        {
            "status": 200,
            "message": "",
            "payload": ["Dockerfile", "path_a/", "path_b/"]
        }
        @apiUse APIHeader
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse ServerError
        """
        return self._safe_wrapper(request, 'get', **kwargs)

    def post(self, request, **kwargs):
        """
        @api {post} /user_space/<str:uuid>/ Create file/directory in user space
        @apiDescription Create a text file or directory in user space. Existing file will be overridden.
        @apiName CreateItemUserSpace
        @apiGroup UserSpace
        @apiVersion 0.1.0
        @apiPermission user

        @apiParam {String} [file] Filename
        @apiParam {String} [path] Path
        @apiParam {String} [content] File content (text only)
        @apiUse APIHeader
        @apiUse Success
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse ServerError
        """
        return self._safe_wrapper(request, 'post', **kwargs)

    def put(self, request, **kwargs):
        """
        @api {put} /user_space/<str:uuid>/ Update file/directory in user space
        @apiDescription Rename file/directory, or change the content of the file. `file` operation may not be mixed with
        `path` operation. `old_file` and `file` together means move/rename the file, and the same applies to `old_path`
        and `path`. Adding a `content` param with `file` present will change the content of that file.
        @apiName UpdateItemUserSpace
        @apiGroup UserSpace
        @apiVersion 0.1.0
        @apiPermission user

        @apiParam {String} [old_file] Old file name
        @apiParam {String} [file] New file name
        @apiParam {String} [content] File content (text only)
        @apiParam {String} [old_path] Old path name
        @apiParam {String} [path] New path name
        @apiUse APIHeader
        @apiUse Success
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse ServerError
        """
        return self._safe_wrapper(request, 'put', **kwargs)

    def delete(self, request, **kwargs):
        """
        @api {delete} /user_space/<str:uuid>/ Delete file/directory in user space
        @apiName DeleteItemUserSpace
        @apiGroup UserSpace
        @apiVersion 0.1.0
        @apiPermission user

        @apiParam {String} [file] Filename
        @apiParam {String} [path] Path
        @apiUse APIHeader
        @apiUse Success
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse ServerError
        """
        return self._safe_wrapper(request, 'delete', **kwargs)


class UserVNCHandler(View):
    http_method_names = ['get']

    def get(self, _, **kwargs):
        """
        @api {get} /vnc/<str:uuid>/ Get VNC pod
        @apiDescription Get a VNC pod where user can edit files in user space in a GUI environment.
        Typically, the full VNC url can be `wss://vnc_host:vnc_port/url_path`. Only secure socket it supported to
        ensure security.
        @apiName GetVNCPod
        @apiGroup UserSpace
        @apiVersion 0.1.0
        @apiPermission user

        @apiSuccess {Object} payload Payload object
        @apiSuccess {String} payload.url_path WebSocket URL path for VNC
        @apiSuccess {String} payload.vnc_password VNC password
        @apiSuccess {String} payload.deployment_name Kubernetes deployment name
        @apiSuccess {String} payload.vnc_host WebSocket host for VNC
        @apiSuccess {Number} payload.vnc_port WebSocket port for VNC
        @apiUse APIHeader
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse ServerError
        """
        try:
            user = kwargs.get('__user', None)
            if user is None:
                raise Exception("Internal exception raised when trying to get `User` object.")
            settings_uuid = kwargs.get('uuid', None)
            if settings_uuid is None:
                raise ValueError
            executor = TaskExecutor.instance(new=False)
            res = {}
            if executor is not None:
                res = executor.get_user_vnc_pod(settings_uuid, user)
            if res:
                response = RESPONSE.SUCCESS
                response['payload'] = res
            else:
                response = RESPONSE.OPERATION_FAILED
            return JsonResponse(response)
        except ValueError:
            return JsonResponse(RESPONSE.INVALID_REQUEST)
        except Exception as ex:
            LOGGER.exception(ex)
            return JsonResponse(RESPONSE.SERVER_ERROR)
