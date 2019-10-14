import json
import uuid

from django.test import TestCase
from api.common import RESPONSE


class TestUserModel(TestCase):
    def setUp(self):
        post_data = {'username': '123', 'password': '123', 'email': '123'}
        self.client.post('/user/', json.dumps(post_data),
                         content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
        self.login_user = {'username': '456',
                           'password': '456', 'email': '456'}
        self.client.post('/user/', json.dumps(self.login_user),
                         content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')

        response = self.client.post('/user/login/', json.dumps(self.login_user),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
        response = json.loads(response.content)
        self.login_user['token'] = response['payload']['token']

    def test_user_login_invalid(self):
        post_data = {'username': '123', 'password': '456'}
        response = self.client.post('/user/login/', data=json.dumps(post_data),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'],
                         RESPONSE.OPERATION_FAILED['status'])

    def test_user_login_no_user(self):
        post_data = {'username': '555', 'password': '555'}
        response = self.client.post('/user/login/', data=json.dumps(post_data),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'],
                         RESPONSE.OPERATION_FAILED['status'])

    def test_user_login_invalid_form(self):
        post_data = {'username': '123', 'hahaha': 'hey'}
        response = self.client.post('/user/login/', data=json.dumps(post_data),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.INVALID_REQUEST)

    def test_user_login_success(self):
        post_data = {'username': '123', 'password': '123'}
        response = self.client.post('/user/login/', data=json.dumps(post_data),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    def test_user_signup_invalid_form(self):
        post_data = {'username': '123', 'hahaha': '123', 'email': '123'}
        response = self.client.post('/user/', json.dumps(post_data),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.INVALID_REQUEST)

    def test_user_signup_success(self):
        post_data = {'username': 'abc', 'password': 'abc', 'email': '123'}
        response = self.client.post('/user/', json.dumps(post_data),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.SUCCESS)

    def test_user_get(self):
        response = self.client.get('/user/', HTTP_X_ACCESS_TOKEN=self.login_user['token'],
                                   HTTP_X_ACCESS_USERNAME=self.login_user['username'])
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['payload']['username'],
                         self.login_user['username'])
        self.assertEqual(response['payload']['email'],
                         self.login_user['email'])

    def test_user_delete(self):
        response = self.client.delete(
            '/user/', HTTP_X_ACCESS_TOKEN=self.login_user['token'], HTTP_X_ACCESS_USERNAME=self.login_user['username'])
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.SUCCESS)

    def test_user_put(self):
        put_data = {'email': 'abc', 'password': '12345'}
        response = self.client.put('/user/', HTTP_X_REQUEST_WITH='XMLHttpRequest', data=json.dumps(put_data),
                                   HTTP_X_ACCESS_TOKEN=self.login_user['token'],
                                   HTTP_X_ACCESS_USERNAME=self.login_user['username'])
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.SUCCESS)

    def test_user_logout(self):
        response = self.client.get('/user/logout/', HTTP_X_ACCESS_TOKEN=self.login_user['token'],
                                   HTTP_X_ACCESS_USERNAME=self.login_user['username'])
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.SUCCESS)

    def test_user_logout_invalid_token(self):
        response = self.client.get('/user/logout/', HTTP_X_ACCESS_TOKEN=str(uuid.uuid1()),
                                   HTTP_X_ACCESS_USERNAME=self.login_user['username'])
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.UNAUTHORIZED)
