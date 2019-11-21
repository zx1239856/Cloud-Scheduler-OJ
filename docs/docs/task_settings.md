# Task Settings
The user with `admin` or `super admin` privilege can edit task settings, while normal `user` can only view some basic information, i.e. name, description, creation time and time/memory limit.

## Some Tips when Adding Tasks
Basically, you can click the **New Settings** button in the upper right corner of the `Task Settings` page. Here are some tips concerning the common fallacies that might be involved.

+ `Image` can either be the Docker image you uploaded to the registry, or a public image in [Docker Hub](https://hub.docker.com/).
+ `Persistent Volume` is the PVC containing task files/scripts. You can create PVCs and upload files into it. Please refer to [Storage Management](storage_mgmt.md)
+ `Mount Path` is the path where PVC mentioned above is mounted.
+ `Shell` is the shell used to execute commands. In most cases, it is `/bin/bash`
+ `Commands` are the commands used to execute task.
+ `Working Path` is where task commands are executed.
+ `Task Script Path` is where the task scripts are. The path is relative to `Mount Path`, so please **DO NOT** add a leading slash `/` if you are unclear about what you are doing.
+ `Task Initial File Path` is where the task initial files are, which is similar to `Task Script Path`. Files in this folder will be copied to user space when the latter is created. See [User Space](index.md#user-space) for more details.

!!! tip
    The commands entered in `Commands` are executed in the `Working Path` you specified.


Tasks can be executed via `+ Add Task` button. Other parts of this page are self-explanatory, which is not covered by this document.

## VNC

User can click `VNC` and get a VNC-capable pod to edit files in GUI mode. The Docker image we provided supports Firefox and VSCode.

!!! info
    The VNC pods are created on-the-fly, which means you have to wait for a couple of seconds before you can connect to the pod.