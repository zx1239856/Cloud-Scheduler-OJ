"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# pylint: disable=C0412
import sys
from django.urls import path
from wsocket import views as ws_views
from task_manager import views as task_mgmt_views
from user_model import views as user_views
from user_model.views import login_required, permission_required
from storage import views as storage_views
from monitor import views as monitor_views
from user_space import views as user_space_views
from registry_manager import views as registry_mgmt_views

# pylint: disable=C0103
websocket_urlpatterns = [
    path('terminals/', ws_views.WebSSH),
    path('user_terminals/', ws_views.UserWebSSH)
]

urlpatterns = [
    path('task_settings/', login_required(task_mgmt_views.TaskSettingsListHandler.as_view())),
    path('task_settings/<str:uuid>/', permission_required(task_mgmt_views.TaskSettingsItemHandler.as_view())),
    path('task/', login_required(task_mgmt_views.ConcreteTaskListHandler.as_view())),
    path('task/<str:uuid>/', login_required(task_mgmt_views.ConcreteTaskHandler.as_view())),
    path('user/login/', user_views.UserLogin.as_view()),
    path('user/logout/', login_required(user_views.UserLogout.as_view())),
    path('user/', user_views.UserHandler.as_view()),
    path('pods/', monitor_views.PodListHandler.as_view()),
    path('storage/', storage_views.StorageHandler.as_view()),
    path('storage/upload_file/', storage_views.StorageFileHandler.as_view()),
    path('user_space/<str:uuid>/', login_required(user_space_views.UserSpaceHandler.as_view())),
    path('registry/', registry_mgmt_views.RegistryHandler.as_view()),
    path('registry/<str:repo>/', registry_mgmt_views.RepositoryHandler.as_view()),
    path('registry/upload/', registry_mgmt_views.RepositoryHandler.as_view()),
    path('registry/<str:repo>/<str:tag>/', registry_mgmt_views.RepositoryHandler.as_view())
]


RUNNING_DEV_SERVER = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')
if RUNNING_DEV_SERVER:
    from task_manager.executor import TaskExecutor
    executor = TaskExecutor.instance()
    executor.start()
