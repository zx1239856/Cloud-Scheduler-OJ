"""
Unit test for websocket
"""
import time
import pytest
from channels.testing import WebsocketCommunicator
import mock
import wsocket
from wsocket.views import WebSSH, UserWebSSH
from user_model.models import UserModel, UserType
from task_manager.models import TaskSettings
from .common import MockWSClient


def mock_stream(_p0, _p1, _p2, **_):
    return MockWSClient()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_ssh_connect():
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


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_ssh_connect_auth_failed():
    with mock.patch.object(wsocket.views, 'stream', mock_stream):
        communicator = WebsocketCommunicator(WebSSH, "/terminals/?pod=none&shell=/bin/sh")
        connected, _ = await communicator.connect()
        assert connected
        _ = UserModel.objects.create(username='admin', user_type=UserType.ADMIN, uuid='uuid', password='pass',
                                     salt='salt', email='email@email.com', token='my_only_token',
                                     token_expire_time=round(time.time()) + 100)
        _ = await communicator.send_to('admin@error_token')
        response = await communicator.receive_from()
        assert response == 'Authentication failed.'
        await communicator.disconnect()


@pytest.mark.asyncio
async def test_ssh_connect_invalid():
    communicator = WebsocketCommunicator(WebSSH, "/terminals/?pod=none&shell=/bin/bad-sh")
    connected, _ = await communicator.connect()
    assert connected
    response = await communicator.receive_from()
    assert response == "\nInvalid request."
    await communicator.disconnect()


@pytest.mark.asyncio
async def test_user_ssh_connect_invalid_req():
    communicator = WebsocketCommunicator(UserWebSSH, "/user_terminals/")
    connected, _ = await communicator.connect()
    assert connected
    response = await communicator.receive_from()
    assert response == "\nInvalid request."
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_user_ssh_user_or_task_not_exist():
    communicator = WebsocketCommunicator(UserWebSSH, "/user_terminals/?uuid=2000&token=2000&username=200")
    connected, _ = await communicator.connect()
    assert connected
    response = await communicator.receive_from()
    assert response == "\nFailed to process."
    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_user_ssh_executor_none(*_):
    _ = UserModel.objects.create(username='admin', user_type=UserType.ADMIN, uuid='uuid', password='pass',
                                 salt='salt', email='email@email.com', token='my_only_token',
                                 token_expire_time=round(time.time()) + 100)
    _ = TaskSettings.objects.create(name='test', uuid='my_uuid', description='', container_config='{}',
                                    time_limit=1, replica=1, ttl_interval=1, max_sharing_users=1)
    with mock.patch.object(wsocket.views, 'stream', mock_stream):
        communicator = WebsocketCommunicator(UserWebSSH,
                                             "/user_terminals/?uuid=my_uuid&token=my_only_token&username=admin")
        connected, _ = await communicator.connect()
        assert connected
        response = await communicator.receive_from()
        assert response == 'Internal server error occurred.\n'
        await communicator.disconnect()


def mock_connect(*_):
    class Conn:
        class Root:
            @staticmethod
            def get_user_space_pod(*_):
                return 'pod'

        root = Root()

    return Conn()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_user_ssh_executor_normal(*_):
    _ = UserModel.objects.create(username='admin', user_type=UserType.ADMIN, uuid='uuid', password='pass',
                                 salt='salt', email='email@email.com', token='my_only_token',
                                 token_expire_time=round(time.time()) + 100)
    _ = TaskSettings.objects.create(name='test', uuid='my_uuid', description='', container_config='{}',
                                    time_limit=1, replica=1, ttl_interval=1, max_sharing_users=1)
    with mock.patch.object(wsocket.views, 'stream', mock_stream):
        wsocket.views.connect = mock_connect
        communicator = WebsocketCommunicator(UserWebSSH,
                                             "/user_terminals/?uuid=my_uuid&token=my_only_token&username=admin")
        connected, _ = await communicator.connect()
        assert connected
        response = await communicator.receive_from()
        assert response == 'Hello from WebSocket!\n'
        _ = await communicator.send_to('hello')
        await communicator.disconnect()
