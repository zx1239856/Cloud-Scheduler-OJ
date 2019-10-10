"""
View handler for WebSocket
"""
from channels.generic.websocket import WebsocketConsumer
from django.http.request import QueryDict
from django.utils.six import StringIO
from threading import Thread
import os
import socket
import websocket as webskt
import json
import time
import ssl

class SSH:
    def __init__(self, websocket):
        self.websocket = websocket
        self.ssh = None
        webskt.enableTrace(False)

    def connect(self):
        try:
            token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IlFScWI0YlJQX09JakNPSDA5bHVqYzEtS0JTazc4MDlRS3Mxak1YU2lGNlEifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tcWZ2ejQiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjBkNGNkZjk3LTU0MWUtNGQ1NC05YzA3LTU5M2VlNzI3ZjcxZiIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.MHh7b_JNRsL5YFQPt_VE3Aa47ZG37GyHAKORXSH_wVJMqJqs0fiBcL1AKwgXjduAjLs9mPE2iP69uSjkH77UABrNtK0o3ZWgGvG7MPHZ7vAOnMCWI6OGu0EsxnFCoR9HFH5fuKdvOoDPnv2JUWoiowffuGhwDXuPFl67X0R0w4KZtxqGikUEnZMJgm0Nc77-DuhjYjAS1ykc5mCJ01MfO429BuekgATw4WAv4uQhYtFBQ_HpI3_u4l5f8xRt9ewNTs75nrNORvRDilwpFFV0GpXzNMxoh-UbGRmh_UCRZN5RubQIOPgQlJy26kgxRAq_0DYuh5TSpDC1-nVNhlcTqQ"
            pod = "wordpress-5b886cf59b-j64lg"
            exec_command = "/bin/bash"
            url = "wss://inftyloop.tech:6443/api/v1/namespaces/default/pods/%s/exec?command=%s&stderr=true&stdin=true&stdout=true&tty=true" % (pod, exec_command)
            header = "Authorization: Bearer " + token
            self.ssh = webskt.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
            self.ssh.connect(url,header=[header])
            Thread(target=self.django_to_websocket).start()
        except socket.timeout:
            self.websocket.close()
            self.close()
        except Exception as e:
            print(e)
            self.close()

    def django_to_ssh(self, data):
        try:
            self.ssh.send_binary(b'\0' + bytearray(data, 'utf-8'))
        except Exception as e:
            print(e)
            self.close()

    def django_to_websocket(self):
        try:
            while True:
                time.sleep(0.01)
                data = self.ssh.recv().decode('utf-8')
                if(len(data) > 0):
                    self.websocket.send(data)
        except Exception as e:
            print(e)
            self.close()

    def close(self):
        if(self.ssh is not None):
            self.ssh.close()
        self.websocket.close()


class WebSSH(WebsocketConsumer):
    """Actual handler for SSH"""
    def connect(self):
        """Open connection to SSH"""
        self.accept()
        query_string = self.scope.get('query_string')
        ssh_args = QueryDict(query_string=query_string, encoding='utf-8')

        self.ssh = SSH(websocket=self)

        self.ssh.connect()

    def disconnect(self, close_code):
        """Disconnect from SSH"""
        try:
            self.ssh.close()
        except:
            pass

    def receive(self, text_data=None, bytes_data=None):
        """Pass text content to remote shell"""
        if text_data is not None:
            self.ssh.django_to_ssh(text_data)