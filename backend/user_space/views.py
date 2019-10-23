"""
View handler for user_space
"""

import logging
import json
from django.http import JsonResponse
from django.views import View
from kubernetes.client import CoreV1Api
from kubernetes.stream import stream
from kubernetes.stream.ws_client import ERROR_CHANNEL
from api.common import RESPONSE
from task_manager.executor import TaskExecutor, getKubernetesAPIClient
from task_manager.models import TaskSettings
from config import KUBERNETES_NAMESPACE

LOGGER = logging.getLogger(__name__)


class UserSpaceHandler(View):
    http_method_names = ['get', 'post', 'put', 'delete']

    @staticmethod
    def _safe_wrapper(fn, request, **kwargs):
        response = None
        api = CoreV1Api(getKubernetesAPIClient())
        try:
            user = kwargs.get('__user', None)
            if user is None:
                raise Exception("Internal exception raised when trying to get `User` object.")
            settings_uuid = kwargs.get('uuid', None)
            if settings_uuid is None:
                raise ValueError
            settings = TaskSettings.objects.get(uuid=settings_uuid)
            username = '{}_{}'.format(user.username, settings.id)
            executor = TaskExecutor.instance()
            if executor is None:
                response = RESPONSE.OPERATION_FAILED
                response['message'] += " Executor is initializing, please wait."
            pod = executor.get_user_space_pod(settings_uuid, user)
            if pod is None:
                response = RESPONSE.OPERATION_FAILED
                response['message'] += " Failed to allocate pod."
            else:
                response = fn(request, api=api, username=username, pod=pod, **kwargs)
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
        def handler(req, **_kwargs):
            params = req.GET
            username = _kwargs['username']
            api = _kwargs['api']
            pod = _kwargs['pod']
            command = ['su', username, '-c']
            cmdlist = []
            file = params.get('file', None)
            path = params.get('path', None)
            if file and path:
                response = RESPONSE.INVALID_REQUEST
                response['message'] += ' You can only choose to list path or cat file.'
            elif not file and not path:
                response = RESPONSE.INVALID_REQUEST
            else:
                if file is not None:
                    cmdlist.append('cat {}'.format(file))
                elif path is not None:
                    cmdlist.append('ls -F {}'.format(path))
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
                    response['payload'] = res.split() if path is not None else res
                else:
                    response = RESPONSE.OPERATION_FAILED
            return response

        return self._safe_wrapper(handler, request, **kwargs)

    def post(self, request, **kwargs):
        def handler(req, **_kwargs):
            query = json.loads(req.body)
            username = _kwargs['username']
            api = _kwargs['api']
            pod = _kwargs['pod']
            file = query.get('file', None)
            path = query.get('path', None)
            content = query.get('content', '')
            if bool(file) ^ bool(path):
                command = ['su', username, '-c']
                cmdlist = []
                LOGGER.debug(content)
                if file is not None:
                    cmdlist.append("cat > {} <<EOF\n{}\nEOF\n".format(file, content))
                elif path is not None:
                    cmdlist.append('mkdir -p {}'.format(path))
                command.append(';'.join(cmdlist))
                LOGGER.debug(command)
                client = stream(api.connect_get_namespaced_pod_exec,
                                pod.metadata.name, KUBERNETES_NAMESPACE, command=command, stderr=True,
                                stdin=False,
                                stdout=True, tty=False, _preload_content=False)
                client.write_stdin(content.encode('unicode-escape').decode())
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
                    response['payload'] = res.split()
                else:
                    response = RESPONSE.OPERATION_FAILED
            else:
                response = RESPONSE.INVALID_REQUEST
            return response

        return self._safe_wrapper(handler, request, **kwargs)

    def put(self, request, **kwargs):
        def handler(req, **_kwargs):
            query = json.loads(req.body)
            username = _kwargs['username']
            api = _kwargs['api']
            pod = _kwargs['pod']
            old_file = query.get('old_file', None)
            old_path = query.get('old_path', None)
            file = query.get('file', None)
            path = query.get('path', None)
            content = query.get('content', None)
            if bool(old_file) ^ bool(old_path) and ((old_file and file and not path) or (old_path and path and not file
                                                                                         and not content)):
                command = ['su', username, '-c']
                cmdlist = []
                if old_file:
                    cmdlist.append('mv {} {}'.format(old_file, file))
                else:
                    cmdlist.append('mv {} {}'.format(old_path, path))
                if content:
                    cmdlist.append("cat > {} <<EOF\n{}\nEOF\n".format(file, content))
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
                    response['payload'] = res.split()
                else:
                    response = RESPONSE.OPERATION_FAILED
            else:
                response = RESPONSE.INVALID_REQUEST
            return response

        return self._safe_wrapper(handler, request, **kwargs)

    def delete(self, request, **kwargs):
        def handler(req, **_kwargs):
            query = json.loads(req.body)
            username = _kwargs['username']
            api = _kwargs['api']
            pod = _kwargs['pod']
            file = query.get('file', None)
            path = query.get('path', None)
            if bool(file) ^ bool(path):
                command = ['su', username, '-c']
                cmdlist = []
                if file is not None:
                    cmdlist.append('rm -f {}'.format(file))
                elif path is not None:
                    cmdlist.append('rm -rf {}'.format(path))
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
                    response['payload'] = res.split()
                else:
                    response = RESPONSE.OPERATION_FAILED
            else:
                response = RESPONSE.INVALID_REQUEST
            return response

        return self._safe_wrapper(handler, request, **kwargs)
