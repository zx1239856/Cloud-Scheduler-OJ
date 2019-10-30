"""
Unit Test for Storage
"""
import json
import os
import mock
from api.common import RESPONSE
import storage.views
from storage.views import StorageFileHandler
from storage.models import FileModel
from .common import MockCoreV1Api, mock_get_k8s_client, TestCaseWithBasicUser, login_test_user

class Mock_WSClient:
    class Mock_Sock:
        def send(self, payload, **kwargs):
            pass
    sock = Mock_Sock()
    def is_open(self):
        return True
    def update(self, timeout, **kwargs):
        pass
    def write_channel(self, channel, data):
        pass
    def peek_stdout(self):
        return True
    def peek_stderr(self):
        return True
    def read_stdout(self):
        return True
    def read_stderr(self):
        return True
    def close(self):
        pass

def mock_stream(_connect_get_namespaced_pod_exec, _name, _namespace, **_kwargs):
    return Mock_WSClient()

def mock_caching(_self, _file_upload, _pvc_name, _path, _md):
    pass

def mock_uploading(_self, _file_name, _pvc_name, _path, _md):
    pass

# pylint: disable=R0904
class TestStorage(TestCaseWithBasicUser):
    def setUp(self):
        super().setUp()
        FileModel.objects.create(filename='test', status=0, hashid='0')
        FileModel.objects.create(filename='test', status=1, hashid='1')
        FileModel.objects.create(filename='test', status=2, hashid='2')
        FileModel.objects.create(filename='test', status=3, hashid='3')
        FileModel.objects.create(filename='test', status=4, hashid='4')

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testGetFileList(self):
        token = login_test_user('admin')
        response = self.client.get('/storage/upload_file/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        self.assertEqual(response['payload']['count'], 5)

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testGetFileListValueError(self):
        token = login_test_user('admin')
        response = self.client.get('/storage/upload_file/', data={'page': -1}, HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    # test getting PVC list
    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testGetPVCListValueError(self):
        token = login_test_user('admin')
        response = self.client.get('/storage/', data={'page': 4}, HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testGetPVCListNoPage(self):
        token = login_test_user('admin')
        response = self.client.get('/storage/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 51)
        self.assertEqual(response['payload']['page_count'], 3)

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testGetPVCListWithPage(self):
        token = login_test_user('admin')
        response = self.client.get('/storage/', data={'page': 3}, HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 51)
        self.assertEqual(response['payload']['page_count'], 3)

    # test creating PVC
    def testCreatePVCRequestError1(self):
        token = login_test_user('admin')
        response = self.client.post('/storage/', data=json.dumps('{invalid_json}'), content_type='application/json', HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreatePVCRequestError2(self):
        token = login_test_user('admin')
        response = self.client.post('/storage/', data=json.dumps({'name': 'pvc'}), content_type='application/json', HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreatePVCRequestError3(self):
        token = login_test_user('admin')
        response = self.client.post('/storage/', data=json.dumps({'capacity': '10Mi'}), content_type='application/json', HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testCreateExistingPVC(self):
        token = login_test_user('admin')
        response = self.client.post('/storage/', data=json.dumps({'name': 'existing-pvc', 'capacity': '10Mi'}),
                                    content_type='application/json',
                                    HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    # test deleting PVC

    def testDeletePVCRequestError(self):
        token = login_test_user('admin')
        response = self.client.delete('/storage/', data=json.dumps({}), content_type='application/json',
                                      HTTP_X_ACCESS_TOKEN=token,
                                      HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testDeletePVCNotExists(self):
        token = login_test_user('admin')
        response = self.client.delete('/storage/', data=json.dumps({'name': 'nonexistent-pvc'}),
                                      HTTP_X_ACCESS_TOKEN=token,
                                      HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testDeletePVC(self):
        token = login_test_user('admin')
        response = self.client.delete('/storage/', data=json.dumps({'name': 'test-pvc'}),
                                      content_type='application/json', HTTP_X_ACCESS_TOKEN=token,
                                      HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    # test uploading files

    def testUploadFileRequestError(self):
        token = login_test_user('admin')
        response = self.client.post('/storage/upload_file/', data={}, HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testUploadFileRequestError2(self):
        token = login_test_user('admin')
        response = self.client.post('/storage/upload_file/', data={'pvcName': "existing-pvc", 'mountPath': "test/"}, HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])
        self.assertEqual(response['message'], "Invalid request. file[] is empty.")

    def testUploadFileRequestError3(self):
        token = login_test_user('admin')
        f = open('test2.txt', 'w')
        f.close()
        f = open('test2.txt', 'r')
        response = self.client.post('/storage/upload_file/', data={'file[]': [f], 'mountPath': "test/"}, HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])
        f.close()
        os.remove('test2.txt')

    def testUploadFileEmptyFiles(self):
        token = login_test_user('admin')
        response = self.client.post('/storage/upload_file/', data={'file[]': [], 'pvcName': 'pvc'}, HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])
        self.assertEqual(response['message'], "Invalid request. file[] is empty.")

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testUploadFilePVCNotExists(self):
        token = login_test_user('admin')
        f = open('test2.txt', 'w')
        f.close()
        f = open('test2.txt', 'r')
        response = self.client.post('/storage/upload_file/',
                                    data={'file[]': [f], 'pvcName': "nonexistent-pvc", 'mountPath': "test/"}, HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])
        self.assertEqual(response['message'], "Operation is unsuccessful. PVC nonexistent-pvc does not exist in namespaced cloud-scheduler.")
        f.close()
        os.remove('test2.txt')

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    @mock.patch.object(storage.views.StorageFileHandler, 'uploading', mock_uploading)
    def testFileUploadPost(self):
        token = login_test_user('admin')
        f = open('test3.txt', 'w')
        f.close()
        f = open('test3.txt', 'r')
        response = self.client.post('/storage/upload_file/',
                                    data={'file[]': [f], 'pvcName': 'test-pvc', 'mountPath': 'test/'}, HTTP_X_ACCESS_TOKEN=token,
                                    HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        f.close()
        os.remove('test3.txt')

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    @mock.patch.object(storage.views.StorageFileHandler, 'uploading', mock_uploading)
    def testRestart(self):
        token = login_test_user('admin')
        response = self.client.put('/storage/upload_file/', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    @mock.patch.object(storage.views, 'get_kubernetes_api_client', mock_get_k8s_client)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    @mock.patch.object(storage.views, 'stream', mock_stream)
    def testFileUploading(self):
        StorageFileHandler().uploading("test3.txt", 'test-pvc', 'test', 'testid')
