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
    def _safe_wrapper(request, op, **kwargs):
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
                params = request.GET
                command = ['su', username, '-c']
                cmdlist = []
                file = params.get('file', None)
                path = params.get('path', None)
                if op != 'get':
                    query = json.loads(request.body)
                    file = query.get('file', None)
                    path = query.get('path', None)
                    content = query.get('content', '')
                if op == 'put':
                    old_file = query.get('old_file', None)
                    old_path = query.get('old_path', None)
                if not bool(file) ^ bool(path):
                    response = RESPONSE.INVALID_REQUEST
                else:
                    if op == 'put' and not ((old_file and file and not path) or (old_path and path and not file
                                                                                 and not content)):
                        response = RESPONSE.INVALID_REQUEST
                    else:
                        if file is not None:
                            if op == 'get':
                                cmdlist.append('cat {}'.format(file))
                            elif op == 'post':
                                cmdlist.append("cat > {} <<EOF\n{}\nEOF\n".format(file, content))
                            elif op == 'delete':
                                cmdlist.append('rm -f {}'.format(file))
                        elif path is not None:
                            if op == 'get':
                                cmdlist.append('ls -F {}'.format(path))
                            elif op == 'post':
                                cmdlist.append('mkdir -p {}'.format(path))
                            elif op == 'delete':
                                cmdlist.append('rm -rf {}'.format(path))
                        if op == 'put':
                            if old_file and old_file != file:
                                cmdlist.append('mv {} {}'.format(old_file, file))
                            elif old_path and old_path == path:
                                cmdlist.append('mv {} {}'.format(old_path, path))
                            if file and content:
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
                            if op == 'get':
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
        return self._safe_wrapper(request, 'get', **kwargs)

    def post(self, request, **kwargs):
        return self._safe_wrapper(request, 'post', **kwargs)

    def put(self, request, **kwargs):
        return self._safe_wrapper(request, 'put', **kwargs)

    def delete(self, request, **kwargs):
        return self._safe_wrapper(request, 'delete', **kwargs)
