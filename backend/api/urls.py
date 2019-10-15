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
from django.urls import path
from wsocket import views as ws_views
from task_manager import views as task_mgmt_views
from user_model import views as user_views
from user_model.views import login_required, permission_required
from storage import views as storage_views
from registry import views as registry_mgmt_views


# pylint: disable=C0103
websocket_urlpatterns = [
    path('terminals/', ws_views.WebSSH),
]

urlpatterns = [
    path('task_settings/', permission_required(task_mgmt_views.TaskSettingsListHandler.as_view())),
    path('task_settings/<str:uuid>/', permission_required(task_mgmt_views.TaskSettingsItemHandler.as_view())),
    path('user/login/', user_views.UserLogin.as_view()),
    path('user/logout/', login_required(user_views.UserLogout.as_view())),
    path('user/', user_views.UserHandler.as_view()),
    path('storage/', storage_views.StorageHandler.as_view()),
    path('storage/upload_file/', storage_views.StorageFileHandler.as_view()),
    path('image_registry/', registry_mgmt_views.RegistryManagementHandler.as_view())
]
