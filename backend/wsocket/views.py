"""
View handler for WebSocket
"""
# pylint: disable=C0411
import socket
import time
import ssl
import logging
import websocket as webskt
from threading import Thread
from channels.generic.websocket import WebsocketConsumer
from django.http.request import QueryDict
from config import KUBERNETES_CLUSTER_TOKEN, KUBERNETES_API_SERVER_URL_WS

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
        self.ssh = None
        webskt.enableTrace(False)

    def connect(self, pod, shell):
        try:
            token = KUBERNETES_CLUSTER_TOKEN
            url = KUBERNETES_API_SERVER_URL_WS + "/api/v1/namespaces/default/pods/%s/exec?command=%s&stderr=true" \
                                                 "&stdin=true&stdout=true&tty=true" % (pod, shell)
            header = "Authorization: Bearer " + token
            self.ssh = webskt.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
            self.ssh.connect(url, header=[header])
            Thread(target=self.django_to_websocket).start()
        except socket.timeout:
            self.close()
        except Exception as e:
            LOGGER.error(e)
            self.close()

    def django_to_ssh(self, data):
        try:
            self.ssh.send_binary(b'\0' + bytearray(data, 'utf-8'))
        except Exception as e:
            LOGGER.error(e)
            self.close()

    def django_to_websocket(self):
        try:
            while True:
                time.sleep(0.01)
                data = self.ssh.recv().decode('utf-8')
                if data:
                    self.websocket.send(data)
        except Exception as e:
            LOGGER.error(e)
            self.close()

    def close(self):
        if self.ssh is not None:
            self.ssh.close()
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
            self.close(code=400)
            return
        self.ssh = SSH(websocket=self)
        self.ssh.connect(pod, shell)

    def disconnect(self, code):
        """Disconnect from SSH"""
        try:
            if self.ssh is not None:
                self.ssh.close()
        except Exception as ex:
            LOGGER.log(ex)

    def receive(self, text_data=None, bytes_data=None):
        """Pass text content to remote shell"""
        if text_data is not None:
            self.ssh.django_to_ssh(text_data)
