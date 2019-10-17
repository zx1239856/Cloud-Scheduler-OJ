"""
Unit Test for Storage
"""
import json
import os
from django.test import TestCase, Client
from api.common import RESPONSE
# from flask import abort, jsonify, Flask, request, Response
"""
app = Flask("mock_server")

storage = {
    "status_code": 201,
    "message": "OK",
    "data": {
        "waybillNumber": "1526351",
        "serviceMode": "10",
        "waybillStatus": "10",
        "deliveryAbbreviationAddress": "深圳",
        "pickupAbbreviationAddress": "深圳"
    },
}

@app.route('/storage/', methods=['GET','POST', 'DELETE'])
def get_task():
    return jsonify(tasks)

app.run(
    host = '0.0.0.0',
    port = 6868,
    debug = True
    )

"""
class TestStorage(TestCase):
    def setUp(self):
        self.client = Client()

    # test getting PVC list
    def testGetPVCList(self):
        response = self.client.get('/storage/')
        self.assertEqual(response.status_code, 200)

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


    def testCreateDuplicatedPVC(self):
        response = self.client.post('/storage/', data=json.dumps({'name':'test-pvc', 'capacity':'10Mi'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.post('/storage/', data=json.dumps({'name':'test-pvc', 'capacity':'10Mi'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])

        response = self.client.delete('/storage/', data=json.dumps({'name': 'test-pvc'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

    # test deleting PVC

    def testDeletePVCRequestError(self):
        response = self.client.delete('/storage/', data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testDeletePVCNotExists(self):
        response = self.client.delete('/storage/', data=json.dumps({'name': 'invalidpvc'}))
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])


    def testCreateAndDeletePVC(self):
        response = self.client.post('/storage/', data=json.dumps({'name':'test-pvc', 'capacity':'10Mi'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        response = self.client.delete('/storage/', data=json.dumps({'name': 'test-pvc'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])



    # test uploading files

    def testUplaodFileRequestError(self):
        response = self.client.post('/storage/upload_file/', data={})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testUplaodFileRequestError2(self):
        response = self.client.post('/storage/upload_file/', data={'name':'xxx'})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    def testUplaodFileRequestError3(self):
        f = open('test.txt', 'w')
        f.close()
        f = open('test.txt', 'r')
        response = self.client.post('/storage/upload_file/', data={'file': f, 'pvcName': 'pvc'})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])
        f.close()
        os.remove('test.txt')

    def testUplaodFilePVCNotExists(self):
        f = open('test2.txt', 'w')
        f.close()
        f = open('test2.txt', 'r')
        response = self.client.post('/storage/upload_file/', data={'file': f, 'pvcName': "invalidpvc", 'mountPath': "test/"})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.OPERATION_FAILED['status'])
        f.close()
        os.remove('test2.txt')

    def testUplaodFile(self):
        response = self.client.post('/storage/', data={'name':'test-pvc', 'capacity':'10Mi'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])

        f = open('test3.txt', 'w')
        f.close()
        f = open('test3.txt', 'r')
        response = self.client.post('/storage/upload_file/', data={'file': f, 'pvcName': 'test-pvc', 'mountPath': 'test/'})
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
        f.close()
        os.remove('test3.txt')

        response = self.client.delete('/storage/', data=json.dumps({'name': 'test-pvc'}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.SUCCESS['status'])
