import json
import random
import bcrypt
from django.test import Client, TestCase
from kubernetes.stream import ws_client
from kubernetes.client.rest import ApiException
from kubernetes.client.api_client import ApiClient
from user_model.models import UserModel, UserType
from api.common import get_uuid


def login_test_user(user):
    client = Client()
    response = client.post('/user/login/', data=json.dumps({
        'username': user,
        'password': user,
    }), content_type='application/json', HTTP_X_REQUEST_WITH='XMLHttpRequest')
    assert response.status_code == 200
    response = json.loads(response.content)
    assert response['status'] == 200
    return response['payload']['token']


def mock_get_k8s_client():
    return 1


class TestCaseWithBasicUser(TestCase):
    def setUp(self):
        self.client = Client()
        # create 3o objects
        self.item_list = []
        salt = bcrypt.gensalt()
        passwd = bcrypt.hashpw('admin'.encode(), salt).decode()
        self.admin = UserModel.objects.create(uuid=str(get_uuid()), username='admin', password=passwd,
                                              email='example@example.com', user_type=UserType.ADMIN, salt=salt.decode())
        passwd = bcrypt.hashpw('user'.encode(), salt).decode()
        self.user = UserModel.objects.create(uuid=str(get_uuid()), username='user', password=passwd,
                                             email='example@example.com', user_type=UserType.USER, salt=salt.decode())


class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ReturnItemsList:
    def __init__(self, item_list):
        self.items = item_list


class MockThread:
    def __init__(self, target, **_):
        self._target = target
        self._running = False

    def start(self):
        self._running = True

    def isAlive(self):
        return self._running


class MockExtensionsV1beta1Api:
    ingress_map = {}

    def __init__(self, _):
        pass

    @staticmethod
    def create_namespaced_ingress(namespace, body):
        name = '{}-{}'.format(namespace, body.metadata['name'])
        if name in MockExtensionsV1beta1Api.ingress_map.keys():
            raise ApiException(status=409)
        else:
            MockExtensionsV1beta1Api.ingress_map[name] = body
            return body

    @staticmethod
    def patch_namespaced_ingress(name, namespace, body):
        name = '{}-{}'.format(namespace, name)
        MockExtensionsV1beta1Api.ingress_map[name] = body
        return body


class MockAppsV1Api:
    pod_map = {}

    def __init__(self, _):
        pass

    @staticmethod
    def read_namespaced_deployment(name, namespace):
        pod = MockAppsV1Api.pod_map.get('{}-{}'.format(name, namespace), None)
        if not pod:
            raise ApiException(status=404)
        else:
            return pod

    @staticmethod
    def create_namespaced_deployment(body, namespace):
        name = '{}-{}'.format(body.metadata.name, namespace)
        if name in MockAppsV1Api.pod_map.keys():
            raise ApiException(status=409)
        MockAppsV1Api.pod_map[name] = body
        return body

    @staticmethod
    def delete_namespaced_deployment(name, namespace):
        if name == 'dep_not_exist':
            raise ApiException(status=404)
        elif name == 'dep_error':
            raise ApiException(status=409)
        print(name, namespace)


class MockCoreV1Api:
    service_map = {}

    def __init__(self, _):
        self.pod_dict = {}
        self.pvc_list = []
        self.api_client = ApiClient()

    def list_namespaced_pod(self, **kwargs):
        label_selector = kwargs.get('label_selector', 'pod_label_selector')
        namespace = kwargs['namespace']
        if label_selector not in self.pod_dict.keys():
            self.pod_dict[label_selector] = 'Pending'
        elif self.pod_dict[label_selector] == 'Pending':
            self.pod_dict[label_selector] = 'Running'
        elif self.pod_dict[label_selector] == 'Running':
            self.pod_dict[label_selector] = 'Succeeded' if random.randint(0, 2) == 0 else 'Failed'
        item_list = [DotDict({
            'status': DotDict({'pod_ip': 'ip', 'phase': self.pod_dict[label_selector]}),
            'metadata': DotDict({
                'namespace': namespace,
                'name': label_selector,
                'creation_timestamp': '000',
                'uid': 'uid_test',
            }),
            'spec':
                DotDict({
                    'node_name': 'test_node',
                    'volumes': [DotDict({}),
                                DotDict({'persistent_volume_claim': DotDict({'claim_name': 'test-pvc-using'})})]
                })
        })]
        return ReturnItemsList(item_list)

    @staticmethod
    def read_namespaced_pod_log(name, namespace, **_):
        return 'Hello world log from pod {} in ns {}'.format(name, namespace)

    @staticmethod
    def delete_namespaced_pod(**_):
        pass

    @staticmethod
    def list_pod_for_all_namespaces(**_):
        item_list = []
        for i in range(0, 51):
            item_list.append(DotDict({
                'status': DotDict({'pod_ip': 'ip_{}'.format(i), 'phase': 'Running'}),
                'metadata':
                    DotDict({
                        'namespace': 'test_ns',
                        'name': 'pod_{}'.format(i),
                        'creation_timestamp': str(i),
                        'uid': 'uid_{}'.format(i),
                    }),
                'spec': DotDict({'node_name': 'test_node'})
            }))
        return ReturnItemsList(item_list)

    @staticmethod
    def list_namespaced_persistent_volume_claim(**_):
        item_list = []
        for i in range(0, 50):
            item_list.append(DotDict({
                'metadata':
                    DotDict({
                        'namespace': 'test-ns',
                        'name': 'pvc_{}'.format(i),
                    }),
                'spec':
                    DotDict({
                        'resources':
                            DotDict({
                                'requests': {'storage': '100Mi'}
                            }),
                        'access_modes': ['ReadWriteMany']
                    }),
                'status':
                    DotDict({
                        'phase': "Bound",
                        'capacity': {'storage': "100Mi"}
                    })
            }))
        item_list.append(DotDict({
            'metadata':
                DotDict({
                    'namespace': 'test-ns',
                    'name': 'pvc_50',
                }),
            'spec':
                DotDict({
                    'resources':
                        DotDict({
                            'requests': {'storage': '100Mi'}
                        }),
                    'access_modes': ['ReadWriteMany']
                }),
            'status':
                DotDict({
                    'phase': "Pending",
                    'capacity': None
                })
        }))
        return ReturnItemsList(item_list)

    @staticmethod
    def delete_namespaced_persistent_volume_claim(name, **_):
        if name == 'nonexistent-pvc':
            raise ApiException(status=404, reason="nonexistent-pvc")

    @staticmethod
    def create_namespace(name, **_):
        pass

    @staticmethod
    def create_namespaced_persistent_volume_claim(namespace, body, **__):
        print(namespace)
        if body.metadata.name == 'existing-pvc':
            raise ApiException(status=409, reason="existing-pvc")

    @staticmethod
    def read_namespaced_persistent_volume_claim(name, *_, **__):
        if name == 'nonexistent-pvc':
            raise ApiException(status=404, reason="nonexistent-pvc")

    @staticmethod
    def read_namespaced_persistent_volume_claim_status(name, **_):
        if name == 'nonexistent-pvc':
            raise ApiException(status=404, reason="nonexistent-pvc")

    @staticmethod
    def create_namespaced_pod(**_):
        pass

    @staticmethod
    def read_namespaced_pod_status(_name, *_, **__):
        if _name == "pod-unreadypvc":
            return DotDict({'status': DotDict({'phase': 'Pending'})})
        return DotDict({'status': DotDict({'phase': 'Running'})})

    def connect_get_namespaced_pod_exec(self, _name, _namespace, _command, **_):
        pass

    @staticmethod
    def create_namespaced_service(body, namespace):
        name = '{}-{}'.format(body.metadata.name, namespace)
        if name in MockCoreV1Api.service_map.keys():
            raise ApiException(status=409)  # mock conflict
        else:
            MockCoreV1Api.service_map[name] = body
            return body


class MockBatchV1Api:
    def __init__(self, _):
        pass

    @staticmethod
    def delete_namespaced_job(**_):
        pass

    @staticmethod
    def create_namespaced_job(**_):
        pass


class MockTaskExecutorNotReady:
    @classmethod
    def instance(cls, **_):
        return None


class MockTaskExecutorWithInternalError:
    @classmethod
    def instance(cls, **_):
        return MockTaskExecutorWithInternalError()

    @staticmethod
    def get_user_vnc_pod(uuid, user):
        # user object is not JSON serializable
        return {'uuid': uuid, 'user': user}


class MockTaskExecutor:
    def __init__(self):
        self.ready = True

    def schedule_task_settings(self, *_, **__):
        pass

    @classmethod
    def instance(cls, **_):
        return MockTaskExecutor()

    @staticmethod
    def get_user_space_pod(*_):
        return DotDict({
            'status': DotDict({'pod_ip': 'ip', 'phase': 'Running'}),
            'metadata': DotDict({
                'namespace': 'test_ns',
                'name': 'test',
                'creation_timestamp': '000',
                'uid': 'uid_test',
            }),
            'spec': DotDict({'node_name': 'test_node'})
        })

    @staticmethod
    def get_user_vnc_pod(uuid, user):
        return {'magic': 19260817, 'uuid': uuid, 'user': user.username}


class MockWSClient:
    def __init__(self, **_):
        self.counter = 1000
        print("Initialized MockWebSocket")
        self.open = True

    def write_stdin(self, data, **_):
        pass

    def read_stdout(self, **_):
        if self.counter > 0:
            self.counter -= 1
            return "Hello from WebSocket!\n"
        else:
            raise Exception("Connection closed by remote server.")

    def is_open(self):
        return self.open

    def close(self, **_):
        self.open = False

    def write_channel(self, *_):
        pass

    def read_channel(self, channel, **_):
        if channel == ws_client.ERROR_CHANNEL:
            return json.dumps({'status': 'Success'})
        else:
            return ''

    def run_forever(self, timeout):
        pass


class MockDXFBase:
    def __init__(self, *_, **__):
        pass

    @staticmethod
    def list_repos(**__):
        return ['test_repo']


class MockDXF:
    def __init__(self, *_, **__):
        pass

    @staticmethod
    def get_digest(*_):
        return ''

    @staticmethod
    def list_aliases(**_):
        return ['test_alias']

    @staticmethod
    def del_blob(*_):
        return True

    @staticmethod
    def push_blob(*_, **__):
        return True

    @staticmethod
    def set_manifest(*_):
        return True


class MockRequest:
    def __init__(self, *args, **_):
        if 'manifests' in args[0]:
            self.url = 'manifests'
        elif 'blobs' in args[0]:
            self.url = 'blobs'
        elif 'tags' in args[0]:
            self.url = 'tags'


def MockUrlOpen(request, **_):
    if request.url == 'manifests':
        return {
            "schemaVersion": 1,
            "name": "test_repo",
            "tag": "[test_alias]",
            "architecture": "amd64",
            "fsLayers": [
                {
                    "blobSum": "sha256:test-latest"
                }
            ],
            "history": [
                {
                    "v1Compatibility": "{\"architecture\":\"amd64\",\"config\":{\"Hostname\":\"\",\"Domainname\":\"\",\"User\":\"\",\"AttachStdin\":false,\"AttachStdout\":false,\"AttachStderr\":false,\"Tty\":false,\"OpenStdin\":false,\"StdinOnce\":false,\"Env\":[\"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"],\"Cmd\":[\"/hello\"],\"ArgsEscaped\":true,\"Image\":\"sha256:a6d1aaad8ca65655449a26146699fe9d61240071f6992975be7e720f1cd42440\",\"Volumes\":null,\"WorkingDir\":\"\",\"Entrypoint\":null,\"OnBuild\":null,\"Labels\":null},\"container\":\"8e2caa5a514bb6d8b4f2a2553e9067498d261a0fd83a96aeaaf303943dff6ff9\",\"container_config\":{\"Hostname\":\"8e2caa5a514b\",\"Domainname\":\"\",\"User\":\"\",\"AttachStdin\":false,\"AttachStdout\":false,\"AttachStderr\":false,\"Tty\":false,\"OpenStdin\":false,\"StdinOnce\":false,\"Env\":[\"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"],\"Cmd\":[\"/bin/sh\",\"-c\",\"#(nop) \",\"CMD [\\\"/hello\\\"]\"],\"ArgsEscaped\":true,\"Image\":\"sha256:a6d1aaad8ca65655449a26146699fe9d61240071f6992975be7e720f1cd42440\",\"Volumes\":null,\"WorkingDir\":\"\",\"Entrypoint\":null,\"OnBuild\":null,\"Labels\":{}},\"created\":\"2019-01-01T01:29:27.650294696Z\",\"docker_version\":\"18.06.1-ce\",\"id\":\"9f5834b25059239faef06a9ba681db7b7c572fc0d87d2b140b10e90e50902b53\",\"os\":\"linux\",\"parent\":\"65b27d3bd74d2cf4ea3aa9e250be6c632f0a347e8abd5485345c55fa6eed0258\",\"throwaway\":true}"
                }
            ]
        }
    elif request.url == 'blobs':
        class MockResponse:
            def __init__(self, response_code, contentLength):
                self.status = response_code
                self.contentLength = contentLength

            def info(self):
                return {
                    'Content-Length': self.contentLength
                }

        return MockResponse(200, '0')
    elif request.url == 'tags':
        return {
            'tags': 'test-latest'
        }
    else:
        return None


def MockUrlOpenErrorResponse(*_, **__):
    class MockResponse:
        def __init__(self, response_code, contentLength):
            self.status = response_code
            self.contentLength = contentLength

        def info(self):
            return {
                'Content-Length': self.contentLength
            }

    return MockResponse(400, '0')


def MockJsonRequest(*_):
    return {
        "schemaVersion": 1,
        "name": "test_repo",
        "tags": ["test_alias"],
        "architecture": "amd64",
        "fsLayers": [
            {
                "blobSum": "sha256:test-latest"
            }
        ],
        "history": [
            {
                "v1Compatibility": "{\"architecture\":\"amd64\",\"config\":{\"Hostname\":\"\",\"Domainname\":\"\",\"User\":\"\",\"AttachStdin\":false,\"AttachStdout\":false,\"AttachStderr\":false,\"Tty\":false,\"OpenStdin\":false,\"StdinOnce\":false,\"Env\":[\"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"],\"Cmd\":[\"/hello\"],\"ArgsEscaped\":true,\"Image\":\"sha256:a6d1aaad8ca65655449a26146699fe9d61240071f6992975be7e720f1cd42440\",\"Volumes\":null,\"WorkingDir\":\"\",\"Entrypoint\":null,\"OnBuild\":null,\"Labels\":null},\"container\":\"8e2caa5a514bb6d8b4f2a2553e9067498d261a0fd83a96aeaaf303943dff6ff9\",\"container_config\":{\"Hostname\":\"8e2caa5a514b\",\"Domainname\":\"\",\"User\":\"\",\"AttachStdin\":false,\"AttachStdout\":false,\"AttachStderr\":false,\"Tty\":false,\"OpenStdin\":false,\"StdinOnce\":false,\"Env\":[\"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\"],\"Cmd\":[\"/bin/sh\",\"-c\",\"#(nop) \",\"CMD [\\\"/hello\\\"]\"],\"ArgsEscaped\":true,\"Image\":\"sha256:a6d1aaad8ca65655449a26146699fe9d61240071f6992975be7e720f1cd42440\",\"Volumes\":null,\"WorkingDir\":\"\",\"Entrypoint\":null,\"OnBuild\":null,\"Labels\":{}},\"created\":\"2019-01-01T01:29:27.650294696Z\",\"docker_version\":\"18.06.1-ce\",\"id\":\"9f5834b25059239faef06a9ba681db7b7c572fc0d87d2b140b10e90e50902b53\",\"os\":\"linux\",\"parent\":\"65b27d3bd74d2cf4ea3aa9e250be6c632f0a347e8abd5485345c55fa6eed0258\",\"throwaway\":true}"
            }
        ]
    }


def MockGetTags(*_):
    return ['test_alias']

def Mock_extract_tar_file(*_):
    return True

def Mock_get_json_from_file(*_):
    return [{
        "RepoTags": ["test_repo:test_repo_tag"],
        "Config": "test_config",
        "Layers": ["test_layer"]
    }]

def Mock_create_manifest(*_):
    return {
        "RepoTags": ["test_repo2:test_repo_tag2"],
        "Config": "test_config2",
        "Layers": ["test_layer2"]
    }

class MockOs:

    class path:
        def __init__(self):
            pass

        def getsize(self, *_):
            return 0

        def join(self, *_):
            return "test_path"

    path = path()


def MockHashfile(*_):
    return "test_digest"
