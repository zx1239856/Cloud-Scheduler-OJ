import json
import uuid
import mock
import bcrypt
from django.test import TestCase
from api.common import RESPONSE
import user_model.views as view
from user_model.models import UserModel, UserType
from .common import TestCaseWithBasicUser, get_uuid, login_test_user


def mock_send_mail(subject, message, from_email, recipient_list,
                   fail_silently=False, auth_user=None, auth_password=None,
                   connection=None, html_message=None):
    print(subject, message, from_email, recipient_list, fail_silently, auth_user, auth_password, connection,
          html_message)
    assert isinstance(recipient_list, list)


def mock_send_mail_fail(subject, message, from_email, recipient_list,
                        fail_silently=False, auth_user=None, auth_password=None,
                        connection=None, html_message=None):
    print(subject, message, from_email, recipient_list, fail_silently, auth_user, auth_password, connection,
          html_message)
    assert isinstance(recipient_list, list)
    raise Exception()


class TestMisc(TestCase):
    def test_get_model(self):
        self.assertTrue(view.get_application_model())
        self.assertTrue(view.get_access_token_model())
        self.assertTrue(view.get_access_token_model(True))
        self.assertTrue(view.get_application_model(True))


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

    def test_user_signup_duplicate(self):
        post_data = {'username': '123', 'password': 'abc', 'email': '123'}
        response = self.client.post('/user/', json.dumps(post_data),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

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

    def test_user_get_no_header(self):
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.UNAUTHORIZED)

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

    def test_user_put_invalid_json(self):
        put_data = 'bad_json'
        response = self.client.put('/user/', HTTP_X_REQUEST_WITH='XMLHttpRequest', data=put_data,
                                   HTTP_X_ACCESS_TOKEN=self.login_user['token'],
                                   HTTP_X_ACCESS_USERNAME=self.login_user['username'])
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.INVALID_REQUEST)

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


class TestSuperAdminApis(TestCaseWithBasicUser):
    def setUp(self):
        super().setUp()
        salt = bcrypt.gensalt()
        passwd = bcrypt.hashpw('su_admin'.encode(), salt).decode()
        self.su_admin = UserModel.objects.create(uuid=str(get_uuid()), username='su_admin', password=passwd,
                                                 email='example@example.com', user_type=UserType.SUPER_ADMIN,
                                                 salt=salt.decode())

    def test_permission(self):
        token = login_test_user('admin')
        response = self.client.get('/user/admin/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.PERMISSION_DENIED)
        response = self.client.get('/user/admin/2/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.PERMISSION_DENIED)

    def test_get_list_admin_invalid_req(self):
        token = login_test_user('su_admin')
        response = self.client.get('/user/admin/?page=0', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.INVALID_REQUEST)

    def test_get_list_admin(self):
        token = login_test_user('su_admin')
        response = self.client.get('/user/admin/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['payload']['count'], 1)
        self.assertEqual(response['payload']['page_count'], 1)
        self.assertEqual(response['payload']['entry'][0]['uuid'], self.admin.uuid)

    @mock.patch.object(view, 'send_mail', mock_send_mail)
    def test_create_admin_user_invalid_req(self):
        token = login_test_user('su_admin')
        response = self.client.post('/user/admin/', 'invalid_json',
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.INVALID_REQUEST)
        response = self.client.post('/user/admin/', json.dumps({'invalid': 'invalid'}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.INVALID_REQUEST)

    @mock.patch.object(view, 'send_mail', mock_send_mail_fail)
    def test_create_admin_user_email_fail(self):
        token = login_test_user('su_admin')
        response = self.client.post('/user/admin/', json.dumps({'username': 'test', 'email': 'test@126.com'}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['message'], "Send email failed. Check your SMTP settings")

    @mock.patch.object(view, 'send_mail', mock_send_mail)
    def test_create_admin_user(self):
        token = login_test_user('su_admin')
        response = self.client.post('/user/admin/', json.dumps({'username': 'test', 'email': 'test@126.com'}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['message'], "Send email success")

    @mock.patch.object(view, 'send_mail', mock_send_mail)
    def test_create_admin_user_duplicate(self):
        token = login_test_user('su_admin')
        response = self.client.post('/user/admin/', json.dumps({'username': 'admin', 'email': 'test@126.com'}),
                                    content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def test_delete_admin(self):
        token = login_test_user('su_admin')
        response = self.client.delete('/user/admin/{}/'.format(self.admin.uuid),
                                      HTTP_X_ACCESS_TOKEN=token,
                                      HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response, RESPONSE.SUCCESS)
        response = self.client.get('/user/admin/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['payload']['count'], 0)

    @mock.patch.object(view, 'send_mail', mock_send_mail)
    def test_change_admin(self):
        token = login_test_user('su_admin')
        response = self.client.put('/user/admin/{}/'.format(self.admin.uuid),
                                   json.dumps({'email': 'test222@126.com',
                                               'password_reset': True}),
                                   content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['message'], "Send email success")
        admin = UserModel.objects.get(uuid=self.admin.uuid)
        self.assertEqual(admin.email, 'test222@126.com')

    @mock.patch.object(view, 'send_mail', mock_send_mail_fail)
    def test_change_admin_mail_fail(self):
        token = login_test_user('su_admin')
        response = self.client.put('/user/admin/{}/'.format(self.admin.uuid),
                                   json.dumps({'password_reset': True}),
                                   content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['message'], "Send email failed. Check your SMTP settings")

    @mock.patch.object(view, 'send_mail', mock_send_mail)
    def test_change_admin_not_exist(self):
        token = login_test_user('su_admin')
        response = self.client.put('/user/admin/{}/'.format('invalid'),
                                   json.dumps({'email': 'test222@126.com',
                                               'password_reset': True}),
                                   content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest',
                                   HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='su_admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])
