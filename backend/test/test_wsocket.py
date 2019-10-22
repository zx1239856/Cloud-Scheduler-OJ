"""
Unit test for websocket
"""
import time
import pytest
from channels.testing import WebsocketCommunicator
import mock
import wsocket
from wsocket.views import WebSSH
from user_model.models import UserModel, UserType


class MockWSClient:
    def __init__(self, **_):
        self.counter = 1000
        print("Initialized MockWebSocket")
        self.open = True

    def write_stdin(self, data, **_):
        pass

    def read_stdout(self, **_):
        if self.counter > 0:
            self.counter -= 1
            return "Hello from WebSocket!\n"
        else:
            raise Exception("Connection closed by remote server.")

    def is_open(self):
        return self.open

    def close(self, **_):
        self.open = False

    def write_channel(self, *_):
        pass

    def read_channel(self, *_):
        return ''


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def testSSHConnect():
    def mock_stream(_p0, _p1, _p2, **_):
        return MockWSClient()

    with mock.patch.object(wsocket.views, 'stream', mock_stream):
        communicator = WebsocketCommunicator(WebSSH, "/terminals/?pod=none&shell=/bin/sh")
        connected, _ = await communicator.connect()
        assert connected
        _ = UserModel.objects.create(username='admin', user_type=UserType.ADMIN, uuid='uuid', password='pass',
                                     salt='salt', email='email@email.com', token='my_only_token',
                                     token_expire_time=round(time.time()) + 100)
        _ = await communicator.send_to('admin@my_only_token')
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
