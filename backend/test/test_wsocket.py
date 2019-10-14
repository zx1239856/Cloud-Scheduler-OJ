"""
Unit test for websocket
"""
import mock
import pytest
from channels.testing import WebsocketCommunicator
import wsocket
from wsocket.views import WebSSH


class MockWebSocket:
    def __init__(self, **_):
        self.counter = 100
        print("Initialized MockWebSocket")

    def connect(self, url, **_):
        print("MockWebSocket connected url {}".format(url))

    def send_binary(self, binary, **_):
        assert binary == (b'\0' + bytearray('Hello world', 'utf-8'))

    def recv(self, **_):
        if self.counter > 0:
            self.counter -= 1
            return "Hello from WebSocket!\n".encode('utf8')
        else:
            raise Exception("Connection closed by remote server.")

    def close(self, **_):
        pass


@pytest.mark.asyncio
async def testSSHConnect():
    with mock.patch.object(wsocket.views.webskt, 'WebSocket', MockWebSocket):
        communicator = WebsocketCommunicator(WebSSH, "/terminals/?pod=none&shell=/bin/sh")
        connected, _ = await communicator.connect()
        assert connected
        response = await communicator.receive_from()
        assert response == 'Hello from WebSocket!\n'
        await communicator.send_to('Hello world')
        await communicator.disconnect()


@pytest.mark.asyncio
async def testSSHConnectInvalid():
    communicator = WebsocketCommunicator(WebSSH, "/terminals/?pod=none&shell=/bin/bad-sh")
    connected, _ = await communicator.connect()
    assert connected
    response = await communicator.receive_from()
    assert response == "\nInvalid request."
    await communicator.disconnect()
