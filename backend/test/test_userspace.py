import json
import mock
from kubernetes.stream import ws_client
from api.common import RESPONSE
import user_space.views as views
from task_manager.models import TaskSettings
from .common import login_test_user, TestCaseWithBasicUser, MockCoreV1Api, MockTaskExecutor, MockWSClient, \
    MockTaskExecutorNotReady, MockTaskExecutorWithInternalError


class MockWsClientUserSpace(MockWSClient):
    def read_stdout(self, **_):
        return 'app\ntest\nmain.cpp'


class MockWsClientWithErrors(MockWSClient):
    def read_channel(self, channel, **_):
        if channel == ws_client.ERROR_CHANNEL:
            return json.dumps({'status': 'Failure'})
        else:
            return ''


def mock_stream(_p0, _p1, _p2, **_):
    return MockWsClientUserSpace()


def mock_bad_stream(_p0, _p1, _p2, **_):
    return MockWsClientWithErrors()


class MockNullPodExecutor(MockTaskExecutor):
    @classmethod
    def instance(cls, **_):
        return MockNullPodExecutor()

    @staticmethod
    def get_user_space_pod(*_):
        return None


@mock.patch.object(views, 'CoreV1Api', MockCoreV1Api)
@mock.patch.object(views, 'stream', mock_stream)
class TestUserSpace(TestCaseWithBasicUser):
    def setUp(self):
        super().setUp()
        self.task_settings = TaskSettings.objects.create(uuid='my_uuid', name="task_0",
                                                         description="test",
                                                         container_config=json.dumps(
                                                             {"meta": "meta_string_0"}),
                                                         ttl_interval=3, replica=3, time_limit=5,
                                                         max_sharing_users=1)

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_get_files_invalid_request(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutorNotReady)
    def test_null_executor(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/?file=test', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutorNotReady)
    def test_null_executor_space_reset(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/reset/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutorWithInternalError)
    def test_space_reset_server_error(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/reset/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_space_reset_task_not_found(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/not_exist/reset/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_space_reset_task_success(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/reset/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    @mock.patch.object(views, 'TaskExecutor', MockNullPodExecutor)
    def test_null_pod(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/?file=test', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_invalid_task_settings(self):
        token = login_test_user('admin')
        response = self.client.post('/user_space/invalid_uuid/', data='invalid_json',
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_post_files_invalid_request(self):
        token = login_test_user('admin')
        response = self.client.post('/user_space/my_uuid/', data='invalid_json',
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_put_files_invalid_request(self):
        token = login_test_user('admin')
        response = self.client.put('/user_space/my_uuid/', data=json.dumps({
            'old_file': 'old_file',
            'path': 'path'
        }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_file_crud(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/?file=~/a.cpp',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['payload'], 'app\ntest\nmain.cpp')

        response = self.client.post('/user_space/my_uuid/', data=json.dumps({'file': 'file'}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.put('/user_space/my_uuid/', data=json.dumps({'file': 'file',
                                                                            'old_file': 'old',
                                                                            'content': 'content'}),
                                   content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.delete('/user_space/my_uuid/', data=json.dumps({'file': 'file'}),
                                      content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                      HTTP_X_ACCESS_TOKEN=token,
                                      HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_path_crud(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/?path=~/a.cpp',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['payload'], 'app\ntest\nmain.cpp'.split())

        response = self.client.post('/user_space/my_uuid/', data=json.dumps({'path': 'path'}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.put('/user_space/my_uuid/', data=json.dumps({'old_path': 'old',
                                                                            'path': 'new'}),
                                   content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.delete('/user_space/my_uuid/', data=json.dumps({'path': 'file'}),
                                      content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                      HTTP_X_ACCESS_TOKEN=token,
                                      HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue(response['status'], RESPONSE.SUCCESS['status'])

    @mock.patch.object(views, 'stream', mock_bad_stream)
    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_command_failure(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/?path=~/a.cpp',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertTrue(response['status'], RESPONSE.OPERATION_FAILED['status'])
        self.assertTrue(response['payload'], 'app\ntest\nmain.cpp'.split())

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
    def test_user_vnc_handler(self):
        token = login_test_user('admin')
        response = self.client.get('/vnc/my_uuid/',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['payload']['magic'], 19260817)

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutorNotReady)
    def test_user_vnc_handler_executor_not_ready(self):
        token = login_test_user('admin')
        response = self.client.get('/vnc/my_uuid/',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutorWithInternalError)
    def test_user_vnc_handler_executor_server_err(self):
        token = login_test_user('admin')
        response = self.client.get('/vnc/my_uuid/',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])

    @mock.patch.object(views, 'TaskExecutor', MockTaskExecutorWithInternalError)
    def test_user_space_server_err(self):
        token = login_test_user('admin')
        response = self.client.get('/user_space/my_uuid/?file=test', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])
