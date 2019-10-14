"""
For shared storage management
"""
import tarfile
from tempfile import TemporaryFile
from django.views import View
from django.http import JsonResponse
from kubernetes import client
from kubernetes.stream import stream
from api.common import RESPONSE

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

    def post(self, request, **_):
        """
        @api {post} /storage_manager/ Create a PV claim
        @apiName CreatePVC
        @apiGroup StorageManager
        @apiVersion 0.1.0
        @apiParamExample {json} Request-Example:
        {
            "name": "new_pvc_name",
            "capacity": "1Gi"
        }
        @apiParam {String} name Name of the PVC
        @apiParam {String} required capacity for storage
        @apiSuccess {Object} payload Success payload is empty
        @apiUse Success
        @apiUse AlreadyExists
        """
        request.encoding = 'utf-8'
        if request.POST:
            if 'name' in request.POST:
                pvc_name = request.name
            else:
                pvc_name = "default-pvc"
            if 'capacity' in request.POST:
                pvc_capacity = request.capacity
            else:
                pvc_capacity = "100Mi"

        config_k8s_client()
        api_instance = client.CoreV1Api()
        # Create Specific Namespaces
        try:
            api_instance.create_namespace(client.V1Namespace(api_version="v1", kind="Namespace", metadata=client.V1ObjectMeta(name="storage-manage", labels={"name":"storage-manage"})))
        except Exception:
            pass
        body = client.V1PersistentVolumeClaim(api_version="v1", kind="PersistentVolumeClaim", \
                                            metadata=client.V1ObjectMeta(name=pvc_name, namespace="storage-manage"), \
                                            spec=client.V1PersistentVolumeClaimSpec(access_modes=["ReadWriteMany"], resources=client.V1ResourceRequirements(requests={"storage": pvc_capacity}), storage_class_name="csi-cephfs"))
        try:
            api_instance.create_namespaced_persistent_volume_claim("storage-manage", body)
            response = RESPONSE.SUCCESS
            response['name'] = pvc_name
        except Exception:
            response = RESPONSE.OPERATION_FAILED
            response['name'] = pvc_name
        return JsonResponse(response)


    def delete(self, request, **_):
        """
        @api {delete} /storage_manager/ Delete a PV claim
        @apiName DeletePVC
        @apiGroup StorageManager
        @apiVersion 0.1.0
        @apiParamExample {json} Request-Example:
        {
            "name": "pvc_name"
        }
        @apiParam {String} name Name of the PVC
        @apiUse Success
        """
        pvc_name = 'default-pvc'
        request.encoding = 'utf-8'
        if request.POST:
            if 'name' in request.POST:
                pvc_name = request.name
            else:
                response = RESPONSE.INVALID_REQUEST
                return JsonResponse(response)
        config_k8s_client()
        api_instance = client.CoreV1Api()
        try:
            api_instance.delete_namespaced_persistent_volume_claim(name=pvc_name, namespace='storage-manage')
            response = RESPONSE.SUCCESS
        except Exception:
            response = RESPONSE.OPERATION_FAILED
        response['name'] = pvc_name
        return JsonResponse(response)


class StorageFileHandler(View):
    http_method_names = ['post', 'delete']

    def post(self, request, **_):
        """
        @api {post} /storage_file_manager/ Upload a file into a pvc storage
        @apiName UploadFile
        @apiGroup StorageFileManager
        @apiVersion 0.1.0
        @apiParamExample {json} Request-Example:
        {
            "fileDirectory": "[file_path]",
            "pvcName": "mypvc",
            "path": "/data/"
        }
        @apiParam {String} directory of file to be uploaded
        @apiParam {String} name of the target PVC
        @apiUse Success
        @apiUse Fail
        """
        request.encoding = 'utf-8'
        if request.POST and 'directory' in request.POST and 'pvcName' in request.POST and 'path' in request.POST:
            directory = request.directory
            pvc_name = request.pvcName
            path = request.path
        else:
            response = RESPONSE.INVALID_REQUEST
            return JsonResponse(response)
            #directory = "D:\\test.txt"
            #pvc_name = "test"
            #path = "/data/"

        config_k8s_client()
        api_instance = client.CoreV1Api()

        # create if namespace does not exist
        try:
            api_instance.create_namespace(client.V1Namespace(api_version="v1", kind="Namespace", metadata=client.V1ObjectMeta(name="storage-manage", labels={"name":"storage-manage"})))
        except Exception:
            pass

        # create pod, mount pvc
        try:
            volume = client.V1Volume(name="file-upload-volume", persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name, read_only=False))
            volume_mount = client.V1VolumeMount(name="file-upload-volume", mount_path=path)
            container = client.V1Container(name="file-upload-container", image="nginx:1.7.9", image_pull_policy="IfNotPresent", volume_mounts=[volume_mount])
            pod = client.V1Pod(api_version="v1", kind="Pod", metadata=client.V1ObjectMeta(name="file-upload-pod", namespace="storage-manage"), \
                            spec=client.V1PodSpec(containers=[container], volumes=[volume]))
            api_instance.create_namespaced_pod(namespace="storage-manage", body=pod)
        except Exception:
            pass

        exec_command = ['tar', 'xvf', '-', '-C', path]
        resp = stream(api_instance.connect_get_namespaced_pod_exec, "file-upload-pod", "storage-manage", command=exec_command, \
                        stderr=True, stdin=True, stdout=True, tty=False, _preload_content=False)

        with TemporaryFile() as tar_buffer:
            with tarfile.open(fileobj=tar_buffer, mode='w') as tar:
                tar.add(directory)

            tar_buffer.seek(0)
            commands = []
            commands.append(tar_buffer.read())

            while resp.is_open():
                resp.update(timeout=1)
                if resp.peek_stdout():
                    #print("STDOUT: %s" % resp.read_stdout())
                    pass
                if resp.peek_stderr():
                    #print("STDERR: %s" % resp.read_stderr())
                    pass
                if commands:
                    c = commands.pop(0)
                    resp.write_stdin(c.decode())
                else:
                    break
            resp.close()

        return JsonResponse(RESPONSE.SUCCESS)
