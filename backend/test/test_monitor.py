from uuid import uuid1
import json
import mock
from task_manager.models import TaskSettings
from api.common import RESPONSE
import monitor.views
from .common import loginTestUser, TestCaseWithBasicUser, MockCoreV1Api, mockGetK8sClient


class TestTaskSettings(TestCaseWithBasicUser):
    def setUp(self):
        super().setUp()
        for i in range(0, 30):
            item = TaskSettings.objects.create(uuid=str(uuid1()), name="task_{}".format(i),
                                               description="test",
                                               container_config=json.dumps({"meta": "meta_string_{}".format(i)}),
                                               ttl_interval=3, replica=30 - i, time_limit=5, max_sharing_users=1)
            self.item_list.append(item)

    def testGetPostListInvalidReq(self):
        token = loginTestUser('admin')
        response = self.client.get('/pods/?page=invalid_page', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], RESPONSE.INVALID_REQUEST['status'])

    @mock.patch.object(monitor.views, 'getKubernetesAPIClient', mockGetK8sClient)
    @mock.patch.object(monitor.views, 'CoreV1Api', MockCoreV1Api)
    def testGetPodList(self):
        token = loginTestUser('admin')
        response = self.client.get('/pods/?page=1', HTTP_X_ACCESS_TOKEN=token,
                                   HTTP_X_ACCESS_USERNAME='admin')
        self.assertEqual(response.status_code, 200)
        response = json.loads(response.content)
        self.assertEqual(response['status'], 200)
        self.assertEqual(response['payload']['count'], 51)
        self.assertEqual(response['payload']['page_count'], 3)
