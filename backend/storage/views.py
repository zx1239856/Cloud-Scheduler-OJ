"""
For shared storage management
"""
import os
import time
import logging
import tarfile
from tempfile import TemporaryFile
import json
from threading import Thread
from django.views import View
from django.http import JsonResponse
from kubernetes import client
from kubernetes.stream import stream
from kubernetes.client.rest import ApiException
from api.common import RESPONSE
from config import KUBERNETES_NAMESPACE

LOGGER = logging.getLogger(__name__)

def config_k8s_client():
    """set up connection to k8s cluster"""
    APISERVER = 'https://152.136.222.117:30000'

    # Define the barer token we are going to use to authenticate.
    # See here to create the token:
    # https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/
    Token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tNmQ4MnciLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6IjY1NjNjMTc1LWViNDgtMTFlOS1hYzA2LTUyMGMzOGUyZjVlNSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.UTS6FqgyHxKFT7nWbxzbi3qXf8Xx6zIYg-TXJItpX_u4lPFQB6DwlgBMA16Xv3uImhDK857vfh_jyulqTlFZQTx47T3CzZ0NMxdTPYV6jPqdgxOXLixFWmfkVzsup7HhcTjXo67crxTu5pXlUqfDHmlub_JRdkLK5eHvEBU7-ArNWS-2iaeF-zifwih7A52qfxt-87PkFO76c3GetJ9b9RPu5mtVyMA7CaQoj2MZybKiTfq1C_mLgXsCHNwRpubJSBLdNMI9E6QDG99zV2asOMxMoNClrCDNfD97a702_2d2P-KU11yvM37rzMvaJptRFHuXtO_2ow6s9byez1XSGw"

    # Create a configuration object
    configuration = client.Configuration()

    # Specify the endpoint of your Kube cluster
    configuration.host = APISERVER

    # Security part.
    configuration.verify_ssl = False

    # ssl_ca_cert is the filepath to the file that contains the certificate.
    # configuration.ssl_ca_cert="certificate"

    configuration.api_key = {"authorization": "Bearer " + Token}
    # configuration.api_key["authorization"] = "bearer " + Token
    # configuration.api_key_prefix['authorization'] = 'Bearer'
    # configuration.ssl_ca_cert = 'ca.crt'

    # Create a ApiClient with our config
    client.Configuration.set_default(configuration)

class StorageHandler(View):
    http_method_names = ['get', 'post', 'delete']

    def get(self, request, **_):
        """
        @api {get} /storage/ Get PVC list
        @apiName GetPVCList
        @apiGroup StorageManager
        @apiVersion 0.1.0
        @apiSuccess {Object} payload Response Object
        @apiSuccess {Number} payload.count Count of total PV claims
        @apiSuccess {Object[]} payload.entry List of PVC
        @apiSuccess {String} payload.entry.name PVC name
        @apiSuccess {String} payload.entry.capacity PVC capacity
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """
        config_k8s_client()
        api_instance = client.CoreV1Api()
        try:
            pvc_list = api_instance.list_namespaced_persistent_volume_claim(KUBERNETES_NAMESPACE).items
            payload = {}
            payload['count'] = len(pvc_list)
            payload['entry'] = []
            for pvc in pvc_list:
                payload['entry'].append({'name': pvc.metadata.name, 'capacity': pvc.spec.resources.requests['storage']})
            response = RESPONSE.SUCCESS
            response['payload'] = payload
        except Exception:
            response = RESPONSE.SERVER_ERROR
        return JsonResponse(response)


    def post(self, request, **_):
        """
        @api {post} /storage/ Create a PVC
        @apiName CreatePVC
        @apiGroup StorageManager
        @apiVersion 0.1.0
        @apiParamExample {json} Request-Body-Example:
        {
            "name": "new_pvc_name",
            "capacity": "1Gi"
        }
        @apiParam {String} name Name of the PVC
        @apiParam {String} capacity Required capacity for storage
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """
        query = json.loads(request.body)
        #request.encoding = 'utf-8'
        try:
            pvc_name = query.get('name', None)
            pvc_capacity = query.get('capacity', None)
            assert pvc_name is not None
            assert pvc_capacity is not None
        except Exception:
            return JsonResponse(RESPONSE.INVALID_REQUEST)

        config_k8s_client()
        api_instance = client.CoreV1Api()

        # Create specific namespace
        try:
            api_instance.create_namespace(client.V1Namespace(api_version="v1", kind="Namespace", metadata=client.V1ObjectMeta(name=KUBERNETES_NAMESPACE, labels={"name":KUBERNETES_NAMESPACE})))
        except Exception:
            # namespaces already exists
            pass

        # Create PVC
        PVC_body = client.V1PersistentVolumeClaim(api_version="v1", kind="PersistentVolumeClaim", \
                                            metadata=client.V1ObjectMeta(name=pvc_name, namespace=KUBERNETES_NAMESPACE), \
                                            spec=client.V1PersistentVolumeClaimSpec(access_modes=["ReadWriteMany"], resources=client.V1ResourceRequirements(requests={"storage": pvc_capacity}), storage_class_name="csi-cephfs"))
        try:
            api_instance.create_namespaced_persistent_volume_claim(KUBERNETES_NAMESPACE, PVC_body)
            response = RESPONSE.SUCCESS
        except Exception:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " PVC named {} already exists.".format(pvc_name)

        return JsonResponse(response)


    def delete(self, request, **_):
        """
        @api {delete} /storage/ Delete a PV claim
        @apiName DeletePVC
        @apiGroup StorageManager
        @apiVersion 0.1.0
        @apiParamExample {json} Request-Example:
        {
            "name": "pvc_name"
        }
        @apiParam {String} name Name of the PVC to be deleted
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """
        query = json.loads(request.body)
        #query = request.GET
        try:
            pvc_name = query.get('name', None)
            assert pvc_name is not None
        except Exception:
            return JsonResponse(RESPONSE.INVALID_REQUEST)

        config_k8s_client()
        api_instance = client.CoreV1Api()

        try:
            api_instance.delete_namespaced_persistent_volume_claim(name=pvc_name, namespace='storage-manage')
            response = RESPONSE.SUCCESS
        except Exception:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " PVC {} not found.".format(pvc_name)

        return JsonResponse(response)


class StorageFileHandler(View):
    http_method_names = ['post']

    def post(self, request, **_):
        """
        @api {post} /storage/upload_file/ Upload a file into a pvc storage
        @apiName UploadFile
        @apiGroup StorageManager
        @apiVersion 0.1.0
        @apiParamExample {json} Request-Example:
        {
            "fileDirectory": "../test.txt",
            "pvcName": "mypvc",
            "mountPath": "data/"
        }
        @apiParam {String} fileDirectory directory of the file to be uploaded
        @apiParam {String} pvcName name of the target PVC
        @apiParam {String} mountPath target path in storage
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """

        #request.encoding = 'utf-8'
        query = json.loads(request.body)
        try:
            directory = query.get('fileDirectory', None)
            pvc_name = query.get('pvcName', None)
            path = query.get('mountPath', None)
            assert directory is not None
            assert pvc_name is not None
            assert path is not None
        except Exception:
            response = RESPONSE.INVALID_REQUEST
            return JsonResponse(response)

        # check if directory exists
        if not os.path.exists(directory):
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " File does not exist in {}".format(directory)
            return JsonResponse(response)

        config_k8s_client()
        api_instance = client.CoreV1Api()

        # check if pvc exists
        try:
            api_instance.read_namespaced_persistent_volume_claim_status(name=pvc_name, namespace=KUBERNETES_NAMESPACE)
        except Exception:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " PVC {} does not exist in namespaced {}".format(pvc_name, KUBERNETES_NAMESPACE)
            return JsonResponse(response)

        # create if namespace does not exist
        try:
            api_instance.create_namespace(client.V1Namespace(api_version="v1", kind="Namespace", metadata=client.V1ObjectMeta(name=KUBERNETES_NAMESPACE, labels={"name":KUBERNETES_NAMESPACE})))
        except Exception:
            pass

        uploading = Thread(target=self.uploading, args=(directory, pvc_name, path))
        uploading.start()

        return JsonResponse(RESPONSE.SUCCESS)


    def uploading(self, directory, pvc_name, path):
        """a new thread to create pod and upload file"""
        config_k8s_client()
        api_instance = client.CoreV1Api()
        # create pod running a container with image nginx, bound pvc
        try:
            volume = client.V1Volume(name="file-upload-volume", persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name, read_only=False))
            volume_mount = client.V1VolumeMount(name="file-upload-volume", mount_path='/cephfs-data/')
            container = client.V1Container(name="file-upload-container", image="nginx:1.7.9", image_pull_policy="IfNotPresent", volume_mounts=[volume_mount])
            pod = client.V1Pod(api_version="v1", kind="Pod",
                               metadata=client.V1ObjectMeta(name="file-upload-pod", namespace=KUBERNETES_NAMESPACE), \
                                                            spec=client.V1PodSpec(containers=[container], volumes=[volume]))
            api_instance.create_namespaced_pod(namespace=KUBERNETES_NAMESPACE, body=pod)
            while api_instance.read_namespaced_pod_status("file-upload-pod", KUBERNETES_NAMESPACE).status.phase != "Running":
                time.sleep(1)
        except ApiException as e:
            LOGGER.warning("Kubernetes ApiException %d: %s", e.status, e.reason)
        except ValueError as e:
            LOGGER.warning(e)
        except Exception as e:
            LOGGER.error(e)

        # create filedir
        exec_command = ['mkdir', '/cephfs-data/'+ path]
        resp = stream(api_instance.connect_get_namespaced_pod_exec, "file-upload-pod", KUBERNETES_NAMESPACE, command=exec_command, \
                        stderr=True, stdin=True, stdout=True, tty=False, _preload_content=False)

        exec_command = ['tar', 'xvf', '-', '-C', '/cephfs-data/'+ path]
        resp = stream(api_instance.connect_get_namespaced_pod_exec, "file-upload-pod", KUBERNETES_NAMESPACE, command=exec_command, \
                        stderr=True, stdin=True, stdout=True, tty=False, _preload_content=False)

        with TemporaryFile() as tar_buffer:
            with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
                tar.add(directory)

            tar_buffer.seek(0)
            commands = []
            commands.append(tar_buffer.read())

            while resp.is_open():
                resp.update(timeout=1)
                #if resp.peek_stdout(): print("STDOUT: %s" % resp.read_stdout())
                #if resp.peek_stderr(): print("STDERR: %s" % resp.read_stderr())
                if commands:
                    c = commands.pop(0)
                    resp.write_stdin(c.decode())
                else:
                    break
            resp.close()

        # delete pod when finished
        api_instance.delete_namespaced_pod("file-upload-pod", KUBERNETES_NAMESPACE)

        LOGGER.info("File uploaded successfully.")
