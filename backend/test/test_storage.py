"""
Unit Test for Storage
"""
import json
from django.test import TestCase, Client
from api.common import RESPONSE

class TestStorage(TestCase):
    def setUp(self):
        self.client = Client()


    # test getting PVC list
    """
    def testGetPVCList(self):
        response = self.client.get('/storage/')
        self.assertEqual(response.status_code, 200)
    """

    # test creating PVC

    def testCreatePVCRequestError1(self):
        response = self.client.post('/storage/', data=json.dumps('{invalid_json}'), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreatePVCRequestError2(self):
        response = self.client.post('/storage/', data=json.dumps({'name':'pvc'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testCreatePVCRequestError3(self):
        response = self.client.post('/storage/', data=json.dumps({'capacity':'10Mi'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    """
    def testCreateDuplicatedPVC(self):
        response = self.client.post('/storage/', data=json.dumps({'name':'test-pvc', 'capacity':'10Mi'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.post('/storage/', data=json.dumps({'name':'test-pvc', 'capacity':'10Mi'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

        response = self.client.delete('/storage/', data=json.dumps({'name': 'test-pvc'}))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
    """

    # test deleting PVC

    def testDeletePVCRequestError(self):
        response = self.client.delete('/storage/', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    """
    def testDeletePVCNotExists(self):
        response = self.client.delete('/storage/', data=json.dumps({'name': 'pvc'}))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def testCreateAndDeletePVC(self):
        response = self.client.post('/storage/', data=json.dumps({'name':'test-pvc', 'capacity':'10Mi'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.delete('/storage/', data=json.dumps({'name': 'test-pvc'}))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
    """

    # test uploading files
    """
    def testUplaodFileRequestError(self):
        response = self.client.post('/storage/upload_file/', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testUplaodFileRequestError2(self):
        response = self.client.post('/storage/upload_file/', data=json.dumps({'name':'xxx'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testUplaodFileRequestError3(self):
        response = self.client.post('/storage/upload_file/', data=json.dumps({'fileDirectory': 'xxx', 'pvcName': 'pvc'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])
    """
    """
    def testUplaodFilePVCNotExists(self):
        response = self.client.post('/storage/upload_file/', data=json.dumps({'fileDirectory': 'D:\\hw3.txt', 'pvcName': 'notexistspvc', 'mountPath': 'test/'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

    def testUplaodFile(self):
        response = self.client.post('/storage/', data=json.dumps({'name':'test-pvc', 'capacity':'10Mi'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.post('/storage/upload_file/', data=json.dumps({'fileDirectory': 'D:\\hw3.txt', 'pvcName': 'test-pvc', 'mountPath': 'test/'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.delete('/storage/', data=json.dumps({'name': 'test-pvc'}))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
    """
