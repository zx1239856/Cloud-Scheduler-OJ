"""
Unit Test for TaskManager
"""
from uuid import uuid1
import json
import mock
from django.test import RequestFactory
from task_manager.models import TaskSettings, Task, TASK
import task_manager.views as views
from user_model.models import UserModel, UserType
from api.common import RESPONSE
from .common import loginTestUser, TestCaseWithBasicUser, MockCoreV1Api


class MockTaskExecutor:
    def __init__(self):
        self.ready = True

    def scheduleTaskSettings(self, *_, **__):
        pass

    @classmethod
    def instance(cls, **_):
        return MockTaskExecutor()


class TestTask(TestCaseWithBasicUser):
    @mock.patch.object(views, 'CoreV1Api', MockCoreV1Api)
    def testGetTaskLogs(self):
        settings = TaskSettings.objects.create(uuid='unique_id', name="task_name",
                                               description="test",
                                               container_config=json.dumps({"meta": "meta_string_{}".format(1)}),
                                               ttl_interval=3, replica=3, time_limit=5, max_sharing_users=1)
        token = loginTestUser('admin')
        response = self.client.post('/task/', data=json.dumps({
            'settings_uuid': 'unique_id'
        }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        task = Task.objects.get(settings=settings)
        task.status = TASK.RUNNING
        task.save(force_update=True)
        response = self.client.get('/task/{}/'.format(task.uuid), HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertTrue(response['payload']['log'].startswith('Hello world log from pod'))

    def testGetTaskInvalidReq(self):
        token = loginTestUser('admin')
        response = self.client.get('/task/?page=invalid', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreateTaskFailures(self):
        token = loginTestUser('admin')
        response = self.client.post('/task/', data='invalid_json',
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])
        response = self.client.post('/task/', data=json.dumps({'settings_uuid': 'not_exist'}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def testGetTaskItemFailures(self):
        token = loginTestUser('admin')
        response = self.client.get('/task/{}/'.format('invalid_uuid'),
                                   HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def testDelTaskItemFailures(self):
        token = loginTestUser('admin')
        response = self.client.delete('/task/{}/'.format('invalid_uuid'),
                                      HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def testTaskCRUD(self):
        TaskSettings.objects.create(uuid='my_uuid', name="task_name",
                                    description="test",
                                    container_config=json.dumps({"meta": "meta_string_{}".format(1)}),
                                    ttl_interval=3, replica=3, time_limit=5, max_sharing_users=1)
        token = loginTestUser('admin')
        task_list = []
        # add 30 tasks
        for _ in range(0, 30):
            response = self.client.post('/task/', data=json.dumps({
                'settings_uuid': 'my_uuid'
            }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                        HTTP_X_ACCESS_TOKEN=token,
                                        HTTP_X_ACCESS_USERNAME='admin')
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
            task_list.append(response['payload']['uuid'])
        # get task list
        response = self.client.get('/task/', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 30)
        self.assertEqual(len(response['payload']['entry']), 25)
        response = self.client.get('/task/?page=2', HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 30)
        self.assertEqual(len(response['payload']['entry']), 5)
        # get specific task
        for uuid in task_list:
            response = self.client.get('/task/{}/'.format(uuid),
                                       HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
            self.assertEqual(response['payload']['uuid'], uuid)
        # delete all tasks
        for uuid in task_list:
            response = self.client.delete('/task/{}/'.format(uuid),
                                          HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)


@mock.patch.object(views, 'TaskExecutor', MockTaskExecutor)
class TestTaskSettings(TestCaseWithBasicUser):
    def setUp(self):
        super().setUp()
        for i in range(0, 30):
            item = TaskSettings.objects.create(uuid=str(uuid1()), name="task_{}".format(i),
                                               description="test",
                                               container_config=json.dumps({"meta": "meta_string_{}".format(i)}),
                                               ttl_interval=3, replica=i + 1, time_limit=5, max_sharing_users=1)
            self.item_list.append(item)

    def testPermission(self):
        token = loginTestUser('user')
        response = self.client.get('/task_settings/?page=1&order_by=-name', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='user')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertTrue('container_config' not in response['payload']['entry'][0].keys())
        self.assertTrue('ttl_interval' not in response['payload']['entry'][0].keys())

    def testGetListInvalidReq(self):
        token = loginTestUser('admin')
        response = self.client.get('/task_settings/?page=invalid', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testGetList(self):
        token = loginTestUser('admin')
        response = self.client.get('/task_settings/?page=1&order_by=-name', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 30)
        self.assertEqual(response['payload']['page_count'], 2)
        self.assertEqual(response['payload']['entry'][0]['name'], 'task_9')

    def testGetList2(self):
        token = loginTestUser('admin')
        response = self.client.get('/task_settings/?page=2', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 30)
        self.assertEqual(response['payload']['page_count'], 2)
        self.assertEqual(response['payload']['entry'][0]['name'], 'task_25')
        self.assertEqual(response['payload']['entry'][4]['name'], 'task_29')

    def testCreateItemInvalidReq1(self):
        token = loginTestUser('admin')
        response = self.client.post('/task_settings/', data='{invalid_json}',
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreateItemInvalidReq2(self):
        token = loginTestUser('admin')
        response = self.client.post('/task_settings/',
                                    data=json.dumps({'replica': 3, 'container_config': {}}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreateDuplicateItem(self):
        token = loginTestUser('admin')
        data = {"name": "task_name", "description": "This is a demo test.",
                "container_config": {}, "time_limit": 900, "replica": 2,
                "ttl_interval": 5, "max_sharing_users": 1}
        response = self.client.post('/task_settings/',
                                    data=json.dumps(data),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        response = self.client.post('/task_settings/',
                                    data=json.dumps(data),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def testDeleteNotExist(self):
        token = loginTestUser('admin')
        resp = self.client.delete('/task_settings/{}/'.format('bad_uuid'), HTTP_X_ACCESS_TOKEN=token,
                                  HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content)
        self.assertEqual(resp['status'], RESPONSE.OPERATION_FAILED['status'])

    def testCreateAndDeleteItem(self):
        token = loginTestUser('admin')
        for i in range(0, 20):
            response = self.client.post('/task_settings/',
                                        data=json.dumps({"name": "task_name_{}".format(i),
                                                         "description": "This is a demo test.",
                                                         "container_config": {}, "time_limit": 900, "replica": 2,
                                                         "ttl_interval": 5, "max_sharing_users": 1}),
                                        content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                        HTTP_X_ACCESS_TOKEN=token,
                                        HTTP_X_ACCESS_USERNAME='admin')
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
        response = self.client.get('/task_settings/?page=2', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 50)
        for i in range(0, 20):
            item = response['payload']['entry'][i]
            resp = self.client.delete('/task_settings/{}/'.format(item['uuid']), HTTP_X_ACCESS_TOKEN=token,
                                      HTTP_X_ACCESS_USERNAME='admin')
            self.assertEqual(resp.status_code, 200)
            resp = json.loads(resp.content)
            self.assertEqual(resp['status'], 200)

    def testGetDetailNotExist(self):
        token = loginTestUser('admin')
        response = self.client.get('/task_settings/{}/'.format('invalid_uuid'), HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def testGetDetail(self):
        token = loginTestUser('admin')
        for i in range(0, 30):
            response = self.client.get('/task_settings/{}/'.format(self.item_list[i].uuid), HTTP_X_ACCESS_TOKEN=token,
                                       HTTP_X_ACCESS_USERNAME='admin')
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
            self.assertEqual(response['payload']['uuid'], self.item_list[i].uuid)
            self.assertEqual(response['payload']['name'], self.item_list[i].name)
            self.assertEqual(response['payload']['replica'], self.item_list[i].replica)
            self.assertEqual(response['payload']['container_config'], json.loads(self.item_list[i].container_config))

    def testUpdateInvalidReq(self):
        token = loginTestUser('admin')
        response = self.client.put('/task_settings/{}/'.format(self.item_list[0].uuid),
                                   data='bad_json', content_type='application/json',
                                   HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testUpdateDuplicateName(self):
        token = loginTestUser('admin')
        response = self.client.put('/task_settings/{}/'.format(self.item_list[0].uuid),
                                   data=json.dumps({
                                       'name': self.item_list[1].name
                                   }), content_type='application/json',
                                   HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def testUpdateDoesNotExist(self):
        token = loginTestUser('admin')
        response = self.client.put('/task_settings/{}/'.format('invalid_uuid'),
                                   data=json.dumps({
                                       'name': self.item_list[1].name
                                   }), content_type='application/json',
                                   HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def testUpdate(self):
        token = loginTestUser('admin')
        for i in range(0, 30):
            response = self.client.put('/task_settings/{}/'.format(self.item_list[i].uuid),
                                       data=json.dumps({
                                           'name': 'changed_name_{}'.format(i),
                                           'replica': i
                                       }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                       HTTP_X_ACCESS_TOKEN=token,
                                       HTTP_X_ACCESS_USERNAME='admin')
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
        for i in range(0, 30):
            response = self.client.get('/task_settings/{}/'.format(self.item_list[i].uuid), HTTP_X_ACCESS_TOKEN=token,
                                       HTTP_X_ACCESS_USERNAME='admin')
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
            self.assertEqual(response['payload']['container_config'], json.loads(self.item_list[i].container_config))

        response = self.client.put('/task_settings/{}/'.format(self.item_list[0].uuid),
                                   data=json.dumps({
                                       'container_config': {}
                                   }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        response = self.client.get('/task_settings/{}/'.format(self.item_list[0].uuid), HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['container_config'], {})

        response = self.client.put('/task_settings/{}/'.format(self.item_list[0].uuid),
                                   data=json.dumps({
                                       'description': 'new_description',
                                       'time_limit': 3,
                                       'replica': 2,
                                       'ttl_interval': 100,
                                       'max_sharing_users': 10
                                   }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)

    # Test for server error
    def testServerError(self):
        factory = RequestFactory()
        get = factory.get('/')
        post = factory.post('/')
        put = factory.put('/')
        delete = factory.delete('/')

        view = views.TaskSettingsListHandler.as_view()
        response = view(get)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])
        response = view(post, __user=UserModel(user_type=UserType.USER))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.PERMISSION_DENIED['status'])
        response = view(post)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])

        view = views.TaskSettingsItemHandler.as_view()
        response = view(get)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])
        response = view(put)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])

        view = views.ConcreteTaskListHandler.as_view()
        response = view(get)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])
        response = view(post)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])

        view = views.ConcreteTaskHandler.as_view()
        response = view(get)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])
        response = view(delete)
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SERVER_ERROR['status'])
