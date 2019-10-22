"""
View handler for tree
"""

import logging
import json
from django.http import JsonResponse
from django.views import View
from kubernetes.client import Configuration, ApiClient, configuration
from kubernetes.client.apis import core_v1_api
from kubernetes.stream import stream
from api.common import RESPONSE
from config import KUBERNETES_CLUSTER_TOKEN, KUBERNETES_API_SERVER_URL

LOGGER = logging.getLogger(__name__)

def addPropertiesToJsonResponse(jsonResponse):
    jsonResponse['payload']['directories'] = []
    jsonResponse['payload']['linux'] = []
    jsonResponse['payload']['files'] = []
    jsonResponse['payload']['filecontent'] = ""
    return jsonResponse

class SSH:
    def __init__(self):
        conf = Configuration()
        conf.host = KUBERNETES_API_SERVER_URL
        conf.verify_ssl = False
        conf.api_key = {"authorization": "Bearer " + KUBERNETES_CLUSTER_TOKEN}
        self.api_client = core_v1_api.CoreV1Api(ApiClient(conf))
        configuration.assert_hostname = False
        self.api_response = None

    def connect(self, pod, command, namespace='default'):
        try:
            self.api_response = stream(
                self.api_client.connect_get_namespaced_pod_exec,
                name=pod,
                namespace=namespace,
                command=command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
                _preload_content=True
            )
            print(self.api_response)
            return self.api_response
        except Exception as ex:
            LOGGER.warning(ex)
            return 1

class TreeFilesHandler(View):
    """tree file ports"""
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request):
        podName = request.GET.get('pod')
        namespace = request.GET.get('namespace')
        path = request.GET.get('path')
        filename = request.GET.get('filename')
        print(filename)
        exec_command = [
            '/bin/sh',
            '-c',
            'cd ' + path + '; cat ' + filename
        ]
        ssh = SSH()
        response = ssh.connect(pod=podName, command=exec_command, namespace=namespace)
        jsonResponse = addPropertiesToJsonResponse(RESPONSE.SUCCESS)
        jsonResponse['payload']['filecontent'] = response
        return JsonResponse(jsonResponse)

    def post(self, request):
        try:
            query = json.loads(request.body)
            podName = query.get('pod', None)
            namespace = query.get('namespace', 'default')
            path = query.get('path', './')
            filename = query.get('filename', '')
            exec_command = [
                '/bin/sh',
                '-c',
                'cd ' + path + '; touch ' + filename
            ]
            ssh = SSH()
            ssh.connect(pod=podName, command=exec_command, namespace=namespace)
            jsonResponse = addPropertiesToJsonResponse(RESPONSE.SUCCESS)
            return JsonResponse(jsonResponse)
        except Exception as ex:
            LOGGER.warning(ex)
            return 1

    def put(self, request):
        query = json.loads(request.body)
        podName = query.get('pod', None)
        namespace = query.get('namespace', 'default')
        path = query.get('path', './')
        filename = query.get('filename', '')
        filecontent = query.get('filecontent', '')
        exec_command = [
            '/bin/sh',
            '-c',
            'cd ' + path + ';' +
            'rm ' + filename + ';' +
            'touch ' + filename + ';' +
            'echo ' + '"' + filecontent + '"' + ' >> ' + filename
        ]
        ssh = SSH()
        ssh.connect(pod=podName, command=exec_command, namespace=namespace)
        jsonResponse = addPropertiesToJsonResponse(RESPONSE.SUCCESS)
        return JsonResponse(jsonResponse)

    def delete(self, request):
        query = json.loads(request.body)
        podName = query.get('pod', None)
        namespace = query.get('namespace', 'default')
        path = query.get('path', './')
        filename = query.get('filename', '')
        exec_command = [
            '/bin/sh',
            '-c',
            'cd ' + path + ';' +
            'rm ' + filename
        ]
        ssh = SSH()
        ssh.connect(pod=podName, command=exec_command, namespace=namespace)
        jsonResponse = addPropertiesToJsonResponse(RESPONSE.SUCCESS)
        return JsonResponse(jsonResponse)

class TreeDirectoriesHandler(View):
    http_method_names = ['post', 'delete']

    def post(self, request):
        query = json.loads(request.body)
        podName = query.get('pod', None)
        namespace = query.get('namespace', 'default')
        path = query.get('path', './')
        directoryname = query.get('directoryname', '')
        exec_command = [
            '/bin/sh',
            '-c',
            'cd ' + path + ';' +
            'mkdir ' + directoryname
        ]
        ssh = SSH()
        ssh.connect(pod=podName, command=exec_command, namespace=namespace)
        jsonResponse = addPropertiesToJsonResponse(RESPONSE.SUCCESS)
        return JsonResponse(jsonResponse)

    def delete(self, request):
        query = json.loads(request.body)
        podName = query.get('pod', None)
        namespace = query.get('namespace', 'default')
        path = query.get('path', './')
        directoryname = query.get('directoryname', '')
        exec_command = [
            '/bin/sh',
            '-c',
            'cd ' + path + ';' +
            'rm -rf' + directoryname
        ]
        ssh = SSH()
        ssh.connect(pod=podName, command=exec_command, namespace=namespace)
        jsonResponse = addPropertiesToJsonResponse(RESPONSE.SUCCESS)
        return JsonResponse(jsonResponse)

class TreeHandler(View):
    http_method_names = ['get']

    def get(self, request):
        podName = request.GET.get('pod', None)
        namespace = request.GET.get('namespace', 'default')
        path = request.GET.get('path')
        exec_command = [
            '/bin/sh',
            '-c',
            'cd ' + path + '; ls -F'
        ]
        ssh = SSH()
        response = ssh.connect(pod=podName, command=exec_command, namespace=namespace)
        jsonResponse = addPropertiesToJsonResponse(RESPONSE.SUCCESS)
        nameList = response.split()
        for name in nameList:
            if name[-1] == '/':
                jsonResponse['payload']['directories'].append(name)
            elif name[-1] == '@':
                jsonResponse['payload']['linux'].append(name)
            else:
                jsonResponse['payload']['files'].append(name)
        return JsonResponse(jsonResponse)
