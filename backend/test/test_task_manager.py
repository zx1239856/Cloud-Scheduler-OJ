"""
Unit Test for TaskManager
"""
from uuid import uuid1
import json
import hashlib
from django.test import TestCase, Client
from task_manager.models import TaskSettings
from user_model.models import UserModel, UserType
from api.common import RESPONSE


def loginTestUser(user):
    client = Client()
    response = client.post('/user/login/', data=json.dumps({
        'username': user,
        'password': user,
    }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
    assert response.status_code == 200
    response = json.loads(response.content)
    assert response['status'] == 200
    return response['payload']['token']


class TestTaskSettings(TestCase):
    def setUp(self):
        self.client = Client()
        # create 3o objects
        self.item_list = []
        md5 = hashlib.md5()
        md5.update('adminadmin_salt'.encode('utf8'))
        UserModel.objects.create(username='admin', password=md5.hexdigest(),
                                 email='example@example.com', user_type=UserType.ADMIN, salt='admin_salt')
        md5 = hashlib.md5()
        md5.update('useruser_salt'.encode('utf8'))
        UserModel.objects.create(username='user', password=md5.hexdigest(),
                                 email='example@example.com', user_type=UserType.USER, salt='user_salt')
        for i in range(0, 30):
            item = TaskSettings.objects.create(uuid=str(uuid1()), name="task_{}".format(i), concurrency=30 - i,
                                               task_config={"meta": "meta_string_{}".format(i)})
            self.item_list.append(item)

    def testPermission(self):
        token = loginTestUser('user')
        response = self.client.get('/task_settings/?page=1&order_by=-name', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='user')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.PERMISSION_DENIED['status'])

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
                                    data=json.dumps({'concurrency': 3, 'task_config': {}}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreateDuplicateItem(self):
        token = loginTestUser('admin')
        response = self.client.post('/task_settings/',
                                    data=json.dumps({'name': 'name', 'concurrency': 3, 'task_config': {}}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token, HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        response = self.client.post('/task_settings/',
                                    data=json.dumps({'name': 'name', 'concurrency': 3, 'task_config': {}}),
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
            response = self.client.post('/task_settings/', data=json.dumps({
                'name': 'unique_name_{}'.format(i),
                'concurrency': i + 1,
                'task_config': {
                    'meta': 'my_meta_{}'.format(i)
                }
            }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest', HTTP_X_ACCESS_TOKEN=token,
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
            self.assertEqual(response['payload']['concurrency'], self.item_list[i].concurrency)
            self.assertEqual(response['payload']['task_config'], str(self.item_list[i].task_config))

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
                                       'name': self.item_list[1].name,
                                       'concurrency': 1
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
                                       'name': self.item_list[1].name,
                                       'concurrency': 1
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
                                           'concurrency': i
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
            self.assertEqual(response['payload']['task_config'], str(self.item_list[i].task_config))

        response = self.client.put('/task_settings/{}/'.format(self.item_list[0].uuid),
                                   data=json.dumps({
                                       'task_config': {}
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
        self.assertEqual(response['payload']['task_config'], '{}')
