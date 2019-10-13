"""
For shared storage management
"""
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from kubernetes import client
from kubernetes import config
import os


def login():
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

    return JsonResponse({"message": "successful login"})

def create_pvc(request):
    """
    @api {post} /create_pvc/ Storage POST Method
    @apiName CreatePVC
    @apiGroup Storage
    @apiVersion 0.1.0

    @apiParam {String} name The name of pvc
    @apiSuccess {String} message Success response message
    @apiSuccessExample {text} Success-Response:
    HTTP/1.1 200 OK
    Create PVC: success or fail
    """
    request.encoding = 'utf-8'
    if request.POST and 'name' in request.POST:
        pvc_name = request.name
    else:
        pvc_name = "default-pvc"
    message = "Create PVC: PVC " + pvc_name + " "
    login()
    v1 = client.CoreV1Api()
    try:
        v1.create_namespace(client.V1Namespace(api_version="v1",kind="Namespace",metadata=client.V1ObjectMeta(name="test",labels={"name":"test"})))
    except:
        pass
    body = client.V1PersistentVolumeClaim(api_version="v1", kind="PersistentVolumeClaim",
                                          metadata=client.V1ObjectMeta(name=pvc_name,namespace="test"),
                                          spec=client.V1PersistentVolumeClaimSpec(access_modes=["ReadWriteOnce"],resources=client.V1ResourceRequirements(requests={"storage":"1Gi"}),storage_class_name="csi-cephfs"))
    try:
        v1.create_namespaced_persistent_volume_claim("test",body)
    except:
        return HttpResponse(message + "already exists")
    return HttpResponse(message + "created successfully")