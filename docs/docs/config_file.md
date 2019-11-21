# Configuration File for API Server

In the root directory of `backend` folder, you can find a `config.py` file, in which you have to edit some configurations for production use.

## Configuration Terms
### System Basics
+ `KUBERNETES_CLUSTER_TOKEN` - Kubernetes API Server Auth Token retrieved in [System Setup](setup.md#kubernetes-api-server-setup)
+ `KUBERNETES_API_SERVER_URL` - Kubernetes API Server Base URL retrieved in [System Setup](setup.md#kubernetes-api-server-setup)
+ `KUBERNETES_NAMESPACE` - A Kubernetes namespace which you intend Cloud Scheduler to manage. All resource created will reside in it.
+ `DEBUG` - **MUST** be `False` in production environment for safety
+ `SECRET_KEY` - A random string for secret key
+ `CLOUD_SCHEDULER_API_SERVER_BASE_URL` - Similar to `KUBERNETES_API_SERVER_URL`, but defines the base url of Cloud Scheduler API server (useful in OAuth 2.0 login and redirections)
+ `CEPH_STORAGE_CLASS_NAME` - Name of cephfs shared filesystem, which is the name of corresponding storage class, such as `csi-cephfs`

### User Settings
+ `USER_TOKEN_EXPIRE_TIME` - Timeout for user token to expire in seconds.
+ `USER_SPACE_POD_TIMEOUT` - Timeout for user space pod to expire in seconds.
+ `GLOBAL_TASK_TIME_LIMIT` - Timeout for a task in seconds (hard limit for all tasks, including the creation time of pods).

### System Performance
+ `DAEMON_WORKERS` - Number of thread workers for TTL check
+ `TASK_DISPATCH_WORKERS` - Number of thread workers for task dispatch, execution and monitor
+ `IPC_PORT` - Internal TCP port for IPC communication between ASGI and WSGI server.
!!! warning
    Please select a port that is not occupied in `localhost`.

### Docker Registry

!!! warning
    Only Docker registry V2 is supported. No V1 registry please.
+ `REGISTRY_ADDRESS` - Host of the Docker registry, in the form of `host:port`, such as `registry.dropthu.online:30443`
+ `REGISTRY_V2_API_ADDRESS` - Base URL of Docker V2 registry, such as `https://registry.dropthu.online:30443/v2`

### Database Settings


!!!tip
    For unit test, please enable file DB to accelerate the process. For production, enable MySQL for performance consideration.

Current only following two types of database engines are supported:  

+  SQLite file DB
```python
DATABASES = {
'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3'),
    }
}
```
+ MySQL DB
```python
DATABASE_USER = 'root'
DATABASE_PASSWORD = 'password'
DATABASE_NAME = 'db_name'
DATABASE_HOST = 'db_host'
DATABASE_PORT = 3306
```

### VNC Settings
+ `USER_WEBSHELL_DOCKER_IMAGE` - The Docker image used to create WebShell and WebIDE pods
+ `USER_VNC_DOCKER_IMAGE` - The Docker image used to create pods supporting VNC
+ `USER_VNC_HOST` - A valid host name for VNC, such as `vnc.dropthu.online`, `192.168.1.2`
+ `USER_VNC_WS_PORT` - External port number for VNC (in public network)
+ `USER_VNC_PORT` - Internal port number for VNC (used to create service and ingress in Kubernetes)
+ `USER_VNC_TLS_SECRET` - Name of TLS secret used to secure WebSocket VNC (which is configured in [Nginx Ingress Controller](setup.md#add-a-tls-secret))

### SMTP Settings

+ `EMAIL_USE_TLS` - Whether to enable TLS for SMTP server
+ `EMAIL_USE_SSL` - Whether to enable SLL for SMTP server
!!! tip
    Only one of `EMAIL_USE_TLS` and `EMAIL_USE_SSL` can be `True` 
+ `EMAIL_HOST` - Host of SMTP server 
+ `EMAIL_HOST_USER` - Username to login SMTP
+ `EMAIL_HOST_PASSWORD` - Password to login SMTP
+ `EMAIL_PORT` - Port number of SMTP 
+ `DEFAULT_FROM_EMAIL` - Same as `EMAIL_HOST_USER` by default
+ `SERVER_EMAIL` - Same as `EMAIL_HOST_USER` by default
