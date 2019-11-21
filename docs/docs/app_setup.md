# Setup Examples of Apps
## Docker Registry
The docker registry can be deployed on the Kubernetes cluster configured and consume its Ceph filesystem. Please apply the example `docker_registry.yaml` and `docker_registry_ingress.yaml` in `config` folder of the project. Remember to edit `<your-domain>` and `<your-tls-secret>` to the value you use. The creation of TLS secret is describe in [Add a TLS Secret](setup.md#add-a-tls-secret).

## VNC WebSocket
This functionality is automatically handled by the scheduler. When user request a VNC pod, the scheduler will create the service and ingress needed to proxy TCP flow over WebSocket. A private link and VNC password will be generated and sent to user.

## Promethus
For convenience, it is recommended to use helm to deploy these apps. The tool is quite easy to install, for which you can refer to [Helm Intro](https://helm.sh/docs/intro/).  
After you installed helm, you can refer to [Promethus README](https://github.com/helm/charts/tree/master/stable/prometheus) to install it.
!!! tip
    You can change the settings of `alertmanager.persistentVolume.storageClass`, `pushgateway.persistentVolume.storageClass` and `server.persistentVolume.storageClass` to `csi-cephfs` (or something equivalent) to consume the shared CephFS.
!!! info
    The prometheus server is internally used by Grafana, so there is no need to create ingress for it.

## Grafana

[Grafana](https://grafana.com/) is a beautiful dashboard to view [Prometheus](https://prometheus.io/) statistics and can also be installed by helm. Refer to [Grafana README](https://github.com/helm/charts/tree/master/stable/grafana) for details. Note you need to overwrite the following settings

```yaml
persistence:
  type: pvc
  enabled: true
  storageClassName: csi-cephfs  # or anything equivalent

grafana.ini:
  paths:
    data: /var/lib/grafana/data
    logs: /var/log/grafana
    plugins: /var/lib/grafana/plugins
    provisioning: /etc/grafana/provisioning
  server:
    root_url: https://example.dropthu.online:30443  # external link that you use to access Grafana
  auth.generic_oauth:
    enabled: true
    name: CloudScheduler
    client_id: # client id you generated in Cloud Scheduler
    client_secret: # client secret you generated in Cloud Scheduler
    scopes: read write
    auth_url: <base-url>/oauth/authorize/  # change <base-url> to the real Cloud Scheduler API server URL
    token_url: <base-url>/oauth/access_token/
    api_url: <base-url>/oauth/user_info/
```

You can apply this patch by saving it as `patch.yaml` and execute `helm install stable/grafana -f patch.yaml --name=grafana --namespace=monitor`.

!!!tip
    The `<base-url>` described above is the URL you specified in `config.py` of Cloud Scheduler.
!!!tip
    You can create an OAuth APP in the admin panel of Cloud Scheduler. Remember to set `redirect_uris` as the correct url of Grafana.
