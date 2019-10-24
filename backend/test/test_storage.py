"""
Unit Test for Storage
"""
import json
import os
import mock
from django.test import TestCase, Client
from api.common import RESPONSE
import storage.views
from storage.models import FileModel
from .common import MockCoreV1Api, mockGetK8sClient

class TestStorage(TestCase):
    def setUp(self):
        self.client = Client()
        FileModel.objects.create(filename='test', status=1, hashid='1')
        FileModel.objects.create(filename='test', status=2, hashid='2')
        FileModel.objects.create(filename='test', status=3, hashid='3')
        FileModel.objects.create(filename='test', status=4, hashid='4')

    # test getting PVC list
    @mock.patch.object(storage.views, 'getKubernetesAPIClient', mockGetK8sClient)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testGetPVCList(self):
        response = self.client.get('/storage/')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 51)

    # test creating PVC
    def testCreatePVCRequestError1(self):
        response = self.client.post('/storage/', data=json.dumps('{invalid_json}'), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreatePVCRequestError2(self):
        response = self.client.post('/storage/', data=json.dumps({'name': 'pvc'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreatePVCRequestError3(self):
        response = self.client.post('/storage/', data=json.dumps({'capacity': '10Mi'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(storage.views, 'getKubernetesAPIClient', mockGetK8sClient)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testCreateExistingPVC(self):
        response = self.client.post('/storage/', data=json.dumps({'name': 'existing-pvc', 'capacity': '10Mi'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    # test deleting PVC

    def testDeletePVCRequestError(self):
        response = self.client.delete('/storage/', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(storage.views, 'getKubernetesAPIClient', mockGetK8sClient)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testDeletePVCNotExists(self):
        response = self.client.delete('/storage/', data=json.dumps({'name': 'nonexistent-pvc'}))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    @mock.patch.object(storage.views, 'getKubernetesAPIClient', mockGetK8sClient)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testCreateAndDeletePVC(self):
        response = self.client.post('/storage/', data=json.dumps({'name': 'test-pvc', 'capacity': '10Mi'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.delete('/storage/', data=json.dumps({'name': 'test-pvc'}),
                                      content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    # test uploading files

    def testUploadFileRequestError(self):
        response = self.client.post('/storage/upload_file/', data={})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testUploadFileRequestError2(self):
        response = self.client.post('/storage/upload_file/', data={'name': 'xxx'})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testUploadFileRequestError3(self):
        f = open('test.txt', 'w')
        f.close()
        f = open('test.txt', 'r')
        response = self.client.post('/storage/upload_file/', data={'file': f, 'pvcName': 'pvc'})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])
        f.close()
        os.remove('test.txt')

    @mock.patch.object(storage.views, 'getKubernetesAPIClient', mockGetK8sClient)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testUploadFilePVCNotExists(self):
        f = open('test2.txt', 'w')
        f.close()
        f = open('test2.txt', 'r')
        response = self.client.post('/storage/upload_file/',
                                    data={'file[]': [f], 'pvcName': "nonexistent-pvc", 'mountPath': "test/"})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])
        f.close()
        os.remove('test2.txt')
    """
    @mock.patch.object(storage.views, 'getKubernetesAPIClient', mockGetK8sClient)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testUploadFile(self):
        f = open('test3.txt', 'w')
        f.close()
        f = open('test3.txt', 'r')
        response = self.client.post('/storage/upload_file/',
                                    data={'file[]': [f], 'pvcName': 'test-pvc', 'mountPath': 'test/'})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        f.close()
        os.remove('test3.txt')
    """

    @mock.patch.object(storage.views, 'getKubernetesAPIClient', mockGetK8sClient)
    @mock.patch.object(storage.views, 'CoreV1Api', MockCoreV1Api)
    def testGetFileList(self):
        response = self.client.get('/storage/upload_file/')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
    """
    def testRestart(self):
        response = self.client.put('/storage/upload_file/')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
    """
