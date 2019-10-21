"""
View handler for tree
"""

import logging
from threading import Thread
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.shortcuts import render
from kubernetes.client import Configuration, ApiClient, configuration
from kubernetes.client.apis import core_v1_api
from kubernetes.stream import stream
from api.common import RESPONSE
from config import KUBERNETES_CLUSTER_TOKEN, KUBERNETES_API_SERVER_URL

LOGGER = logging.getLogger(__name__)

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
            print(pod)
            print(namespace)
            resp = self.api_client.read_namespaced_pod(name=pod, namespace=namespace)
            # print(resp)
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

# class TreeFilesHandler:
#     """tree file ports"""

class TreeHandler(View):
    http_method_names = ['get']

    def get(self, request):
        podName = request.GET.get('pod')
        namespace = request.GET.get('namespace')
        exec_command = [
            '/bin/sh',
            '-c',
            'ls -F'
        ]
        ssh = SSH()
        response = ssh.connect(pod=podName, command=exec_command, namespace=namespace)
        jsonResponse = RESPONSE.SUCCESS
        jsonResponse['payload']['directory'] = []
        jsonResponse['payload']['linux'] = []
        jsonResponse['payload']['file'] = []
        nameList = response.split()
        for name in nameList:
            if name[-1] == '/':
                jsonResponse['payload']['directory'].append({'name': name})
            elif name[-1] == '@':
                jsonResponse['payload']['linux'].append({'name': name})
            else:
                jsonResponse['payload']['file'].append({'name': name})
        return JsonResponse(jsonResponse)
