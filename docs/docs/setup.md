# System Setup
## Prerequisites
+ [Kubernetes](https://kubernetes.io/) cluster >= v1.14.3  (Only tested with clusters equal to or newer than this version)
+ A domain you own (To setup VNC websocket)

## Kubernetes API Server Setup
You need to provide Kubernetes API server credentials for Cloud Scheduler to take over.

+ API URL (required) - It's the URL that Cloud Scheduler uses to access the Kubernetes API. Kubernetes
exposes several APIs, we want the "base" URL that is common to all of them,
e.g., `https://kubernetes.example.com` rather than `https://kubernetes.example.com/api/v1`.  
Get the API URL by running this command:   
  
  ```bash
  kubectl cluster-info | grep 'Kubernetes master' | awk '/http/ {print $NF}'
  ```
  
+ CA Certificate (not available for now) - Cloud Scheduler does not validate CA cert of Kubernetes API for now.

+ Token - Cloud Scheduler authenticates against Kubernetes using service tokens. The token used should belong to a service account with `cluster-admin` privileges. To create this service account:

    1. Create a file called `k8s-admin-service-account.yaml` with contents:
    
       ```yaml
       apiVersion: v1
       kind: ServiceAccount
       metadata:
         name: cloud-scheduler-admin
         namespace: kube-system
       ---
       apiVersion: rbac.authorization.k8s.io/v1beta1
       kind: ClusterRoleBinding
       metadata:
         name: cloud-scheduler-admin
       roleRef:
         apiGroup: rbac.authorization.k8s.io
         kind: ClusterRole
         name: cluster-admin
       subjects:
       - apiGroup: rbac.authorization.k8s.io
         kind: Group
         name: system:masters
       ```
    
  2. Apply the service account and cluster role binding to your cluster:
  
     ```bash
     kubectl apply -f k8s-admin-service-account.yaml
     ```

  3. Retrieve the token for the service account:
  
     ```bash
     kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep cloud-scheduler-admin | awk '{print $1}')
     ```
  
     Copy the `<authentication_token>` value from the output:
  
     ```
     Name:         gitlab-admin-token-b5zv4
     Namespace:    kube-system
     Labels:       <none>
     Annotations:  kubernetes.io/service-account.name=gitlab-admin
                   kubernetes.io/service-account.uid=bcfe66ac-39be-11e8-97e8-026dce96b6e8
     
     Type:  kubernetes.io/service-account-token
     
     Data
     ====
     ca.crt:     1025 bytes
     namespace:  11 bytes
     token:      <authentication_token>
     ```

!!! tip
    It is recommended to setup Cloud Scheduler server with Kubernetes API server in the same private network for safety concerns.
     

## Install Ceph

Cloud scheduler employs [Rook](https://rook.io/docs/rook/v1.1/ceph-filesystem.html) Ceph Shared FS as its file system provider. Here is how to deploy.

!!! warning
    There are some known fallacies in the tutorial documents provided by Rook official. Please **DO NOT** follow them if you are unclear about what you are doing.

### Configure Rook Ceph Cluster
1. Download [common.yaml](https://github.com/rook/rook/blob/release-1.1/cluster/examples/kubernetes/ceph/common.yaml) and execute `kubectl apply -f common.yaml` to add resource definitions required for Rook Ceph
2. Use `operator.yaml` provided by us in `config` directory of the project and `kubectl apply -f operator.yaml`, which is a modified version of Rook Ceph operator with optimal configurations
3. Download [cluster.yaml](https://github.com/rook/rook/blob/release-1.1/cluster/examples/kubernetes/ceph/cluster.yaml) and edit
```yaml
mon:
    count: 3  # change this to the number of nodes in your case
```
Afterwards, you can `kubectl apply -f cluster.yaml` and the Ceph cluster will be online in a few minutes.

### Configure Ceph Shared File System
1. Download [filesystem.yaml](https://github.com/rook/rook/blob/release-1.1/cluster/examples/kubernetes/ceph/filesystem.yaml) and edit
```yaml
spec:
  metadataPool:
    replicated:
      size: 3 # change this to the number of nodes in your case

  dataPools:
    - failureDomain: host
      replicated:
        size: 3  # change this to the number of nodes in your case
```
and `kubectl apply -f filesystem.yaml`
2. Download [storageclass.yaml](https://github.com/rook/rook/blob/release-1.1/cluster/examples/kubernetes/ceph/csi/cephfs/storageclass.yaml) and apply it. You may change the name in `metadata`, which is `csi-cephfs` by default. You will need this name when you modify the configuration term `CEPH_STORAGE_CLASS_NAME` of Cloud Scheduler. See [configuration file](config_file.md) for details.

## Nginx Ingress Controller
This controller is the basis for multiple apps such as VNC, Grafana, Docker Registry, etc. Since they are pods/deployments inside Kubernetes cluster, it would be a bad practice to open a port for each one of them. Instead, using Nginx ingress controller and wrapp them as domains and sub paths is an optimal choice.  
Please refer to [Installation Guide](https://kubernetes.github.io/ingress-nginx/deploy/) for details. You may change the service port of Nginx to some other than conventional 80 or 443. Note that WebSocket reverse proxy is enabled by default, thus you do not need to make any further modifications to get it work.

### Add a TLS Secret
You must add a TLS secret to the namespace you want to deploy something, which can be achieved by
```bash
kubectl -n <name-space> create secret tls <secret-name> \
  --cert=<path-to-cert> \
  --key=<path-to-private-key>
```
The cert must be a pem format full-chain TLS cert issued to the domain you own.



## Fill in Config File
Please see [Config File](config_file.md) for details.