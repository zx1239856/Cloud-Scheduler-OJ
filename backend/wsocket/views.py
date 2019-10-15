"""
View handler for WebSocket
"""
# pylint: disable=C0411
import socket
import logging
from threading import Thread
from channels.generic.websocket import WebsocketConsumer
from django.http.request import QueryDict
from kubernetes.client import Configuration, ApiClient
from kubernetes.client.apis import core_v1_api
from kubernetes.stream import stream
from config import KUBERNETES_CLUSTER_TOKEN, KUBERNETES_API_SERVER_URL

SHELL_LIST = [
    '/bin/sh',
    '/bin/bash',
    '/bin/zsh',
    '/bin/csh',
    '/bin/ksh',
    '/bin/fish',
]
LOGGER = logging.getLogger(__name__)


class SSH:
    def __init__(self, websocket):
        self.websocket = websocket
        conf = Configuration()
        conf.host = KUBERNETES_API_SERVER_URL
        conf.verify_ssl = False
        conf.api_key = {"authorization": "Bearer " + KUBERNETES_CLUSTER_TOKEN}
        self.api_client = core_v1_api.CoreV1Api(ApiClient(conf))
        self.api_response = None

    def connect(self, pod, shell):
        try:
            self.api_response = stream(self.api_client.connect_get_namespaced_pod_exec,
                                       pod, 'default', command=[shell], stderr=True, stdin=True,
                                       stdout=True, tty=True, _preload_content=False)
            Thread(target=self.django_to_websocket).start()
        except socket.timeout:
            self.close()
        except Exception as e:
            LOGGER.error(e)
            self.close()

    def django_to_ssh(self, data):
        try:
            if self.api_response is not None and self.api_response.is_open():
                self.api_response.write_stdin(data)
            else:
                self.close()
        except Exception as e:
            LOGGER.error(e)
            self.close()

    def django_to_websocket(self):
        try:
            while True:
                data = self.api_response.read_stdout()
                if data:
                    self.websocket.send(data)
        except Exception as e:
            LOGGER.error(e)
            self.close()

    def close(self):
        if self.api_response is not None:
            self.api_response.close()
        self.websocket.close()


class WebSSH(WebsocketConsumer):
    """Actual handler for SSH"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh = None

    def connect(self):
        """Open connection to SSH"""
        self.accept()
        query_string = self.scope.get('query_string')
        ssh_args = QueryDict(query_string=query_string, encoding='utf-8')
        pod = ssh_args.get('pod', None)
        shell = ssh_args.get('shell', '/bin/sh')
        if pod is None or shell not in SHELL_LIST:
            self.send("\nInvalid request.")
            LOGGER.warning("Invalid request")
            self.close(code=4000)
            return
        self.ssh = SSH(websocket=self)
        self.ssh.connect(pod, shell)

    def disconnect(self, code):
        """Disconnect from SSH"""
        try:
            if self.ssh is not None:
                self.ssh.close()
        except Exception as ex:
            LOGGER.error(ex)

    def receive(self, text_data=None, bytes_data=None):
        """Pass text content to remote shell"""
        if text_data is not None:
            self.ssh.django_to_ssh(text_data)
