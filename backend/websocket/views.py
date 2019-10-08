"""
View handler for WebSocket
"""
from channels.generic.websocket import WebsocketConsumer
from django.http.request import QueryDict
from django.utils.six import StringIO
from threading import Thread
import os
import paramiko
import socket
import json
import time

class SSH:
    def __init__(self, websocket):
        self.websocket = websocket
        self.channel = None

    def connect(self, host, user, password=None, ssh_key=None, port=22, timeout=30,
                term='xterm', pty_width=80, pty_height=24):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(username=user, password=password, hostname=host, port=port, timeout=timeout)

            transport = ssh_client.get_transport()
            self.channel = transport.open_session()
            self.channel.get_pty(term=term, width=pty_width, height=pty_height)
            self.channel.invoke_shell()

            Thread(target=self.django_to_websocket).start()
        except socket.timeout:
            self.websocket.close()
            self.close()
        except Exception as e:
            print(e)
            self.close()

    def resize_pty(self, cols, rows):
        self.channel.resize_pty(width=cols, height=rows)

    def django_to_ssh(self, data):
        try:
            if(self.channel is not None):
                self.channel.send(data)
        except:
            self.close()

    def django_to_websocket(self):
        try:
            while True:
                time.sleep(0.1)
                data = self.channel.recv(1024).decode('utf-8')
                if(len(data) > 0):
                    self.websocket.send(data)
        except:
            self.close()

    def close(self):
        if(self.channel is not None):
            self.channel.close()
        self.websocket.close()


class WebSSH(WebsocketConsumer):
    """Actual handler for SSH"""
    def connect(self):
        """Open connection to SSH"""
        self.accept()
        query_string = self.scope.get('query_string')
        ssh_args = QueryDict(query_string=query_string, encoding='utf-8')

        #width = int(ssh_args.get('width'))
        #height = int(ssh_args.get('height'))
        port = int(ssh_args.get('port'))

        host = ssh_args.get('host')
        user = ssh_args.get('user')
        passwd = ssh_args.get('password')

        self.ssh = SSH(websocket=self)

        ssh_connect_dict = {
            'host': host,
            'user': user,
            'port': port,
            'timeout': 30,
            'password': passwd
        }

        self.ssh.connect(**ssh_connect_dict)

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
