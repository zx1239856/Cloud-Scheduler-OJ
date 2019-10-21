"""
View handler for WebSocket
"""
# pylint: disable=C0411
import socket
import logging
import time
import json
from threading import Thread
from channels.generic.websocket import WebsocketConsumer
from django.http.request import QueryDict
from kubernetes.client import Configuration, ApiClient
from kubernetes.client.apis import core_v1_api
from kubernetes.stream import stream, ws_client
from user_model.models import UserModel, UserType
from user_model.views import TokenManager
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
    def __init__(self, websocket, **kwargs):
        self.websocket = websocket
        self.auth_ok = False
        self.cols = int(kwargs.get('cols', 80))
        self.rows = int(kwargs.get('rows', 24))
        conf = Configuration()
        conf.host = KUBERNETES_API_SERVER_URL
        conf.verify_ssl = False
        conf.api_key = {"authorization": "Bearer " + KUBERNETES_CLUSTER_TOKEN}
        self.api_client = core_v1_api.CoreV1Api(ApiClient(conf))
        self.api_response = None

    def connect(self, pod, shell, namespace='default'):
        try:
            Thread(target=self.django_to_websocket, kwargs={'pod': pod, 'shell': shell, 'namespace': namespace}).start()
        except socket.timeout:
            self.close()
        except Exception as e:
            LOGGER.error(e)
            self.close()

    def django_to_ssh(self, data):
        try:
            if not self.auth_ok:
                ls = data.split('@')
                if len(ls) == 2:
                    username = ls[0]
                    header_token = ls[1]
                    user = UserModel.objects.get(username=username)
                    token = TokenManager.getToken(user)
                    if token == header_token:
                        TokenManager.updateToken(user)
                        self.auth_ok = True
                if not self.auth_ok:
                    self.websocket.send('Authentication failed.')
                    self.close()
            elif self.api_response is not None and self.api_response.is_open():
                self.api_response.write_stdin(data)
            else:
                self.close()
        except Exception as e:
            LOGGER.error(e)
            self.close()

    def django_to_websocket(self, pod, namespace, shell):
        try:
            self.api_response = stream(self.api_client.connect_get_namespaced_pod_exec,
                                       pod, namespace, command=[shell], stderr=True, stdin=True,
                                       stdout=True, tty=True, _preload_content=False)
            self.api_response.write_channel(ws_client.RESIZE_CHANNEL,
                                            json.dumps({"Height": self.rows, "Width": self.cols}))
            while True:
                if self.auth_ok:
                    data = self.api_response.read_stdout()
                    err = self.api_response.read_channel(ws_client.ERROR_CHANNEL)
                    if data:
                        self.websocket.send(data)
                    else:
                        time.sleep(0.01)
                    try:
                        err = json.loads(err.strip())
                        if err['status'] == 'Success':
                            self.websocket.send('shell terminated with exit code 0\n')
                        elif err['status'] == 'Failure':
                            self.websocket.send(err['message'])
                    except ValueError:
                        pass
                else:
                    time.sleep(0.05)
        except Exception as e:
            LOGGER.error(e)
            self.close()

    def close(self):
        if self.api_response is not None and self.api_response.is_open():
            self.api_response.write_stdin("exit\n")
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
        namespace = ssh_args.get('namespace', 'default')
        shell = ssh_args.get('shell', '/bin/sh')
        cols = ssh_args.get('cols', 80)
        rows = ssh_args.get('rows', 24)
        if pod is None or shell not in SHELL_LIST:
            self.send("\nInvalid request.")
            LOGGER.warning("Invalid request")
            self.close(code=4000)
            return
        LOGGER.info("Connecting to pod: {}, namespace: {}".format(pod, namespace))
        self.ssh = SSH(websocket=self, cols=cols, rows=rows)
        self.ssh.connect(pod, shell, namespace)

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
