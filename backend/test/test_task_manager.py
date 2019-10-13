"""
Unit Test for TaskManager
"""
from uuid import uuid1
import json
from django.test import TestCase, Client
from task_manager.models import TaskSettings


class TestTaskSettings(TestCase):
    def setUp(self):
        self.client = Client()
        # create 3o objects
        self.item_list = []
        for i in range(0, 30):
            item = TaskSettings.objects.create(uuid=str(uuid1()), name="task_{}".format(i), concurrency=30 - i,
                                               task_config={"meta": "meta_string_{}".format(i)})
            self.item_list.append(item)

    def testGetList(self):
        response = self.client.get('/task_settings/?page=1&order_by=-name')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 30)
        self.assertEqual(response['payload']['page_count'], 2)
        self.assertEqual(response['payload']['entry'][0]['name'], 'task_9')

    def testGetList2(self):
        response = self.client.get('/task_settings/?page=2')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 30)
        self.assertEqual(response['payload']['page_count'], 2)
        self.assertEqual(response['payload']['entry'][0]['name'], 'task_25')
        self.assertEqual(response['payload']['entry'][4]['name'], 'task_29')

    def testCreateAndDeleteItem(self):
        for i in range(0, 20):
            response = self.client.post('/task_settings/', data=json.dumps({
                'name': 'unique_name_{}'.format(i),
                'concurrency': i + 1,
                'task_config': {
                    'meta': 'my_meta_{}'.format(i)
                }
            }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
        response = self.client.get('/task_settings/?page=2')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 50)
        for i in range(0, 20):
            item = response['payload']['entry'][i]
            resp = self.client.delete('/task_settings/{}/'.format(item['uuid']))
            self.assertEqual(resp.status_code, 200)
            resp = json.loads(resp.content)
            self.assertEqual(resp['status'], 200)

    def testGetDetail(self):
        for i in range(0, 30):
            response = self.client.get('/task_settings/{}/'.format(self.item_list[i].uuid))
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
            self.assertEqual(response['payload']['uuid'], self.item_list[i].uuid)
            self.assertEqual(response['payload']['name'], self.item_list[i].name)
            self.assertEqual(response['payload']['concurrency'], self.item_list[i].concurrency)
            self.assertEqual(response['payload']['task_config'], str(self.item_list[i].task_config))

    def testUpdate(self):
        for i in range(0, 30):
            response = self.client.put('/task_settings/{}/'.format(self.item_list[i].uuid),
                                       data=json.dumps({
                                           'name': 'changed_name_{}'.format(i),
                                           'concurrency': i
                                       }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
        for i in range(0, 30):
            response = self.client.get('/task_settings/{}/'.format(self.item_list[i].uuid))
            self.assertEqual(response.status_code, 200)
            response = json.loads(response.content)
            self.assertEqual(response['status'], 200)
            self.assertEqual(response['payload']['task_config'], str(self.item_list[i].task_config))
