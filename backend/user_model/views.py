"""
API for user module
"""

import hashlib
import time
import uuid

from django.http import JsonResponse
from django.views import View
from user_model.models import UserModel, UserStatus
from . import responses


class UserLogin(View):
    """User login view"""

    def get(self, request):
        """get request"""
        form = request.GET
        return self.handle_login(form)

    def post(self, request):
        """post request"""
        form = request.POST
        return self.handle_login(form)

    @staticmethod
    def handle_login(form):
        """login api"""
        print(form.keys())
        if not set(['username', 'password']) <= set(form.keys()):
            return JsonResponse(responses.RESPONSE_INVALID_FORM)

        username = form['username']
        password = form['password']

        users = UserModel.objects.filter(username=username)

        if not users:
            return JsonResponse(responses.RESPONSE_INVALID_USERNAME_OR_PASSWORD)

        salt = users[0].salt

        md5 = hashlib.md5()
        md5.update((password + salt).encode('utf-8'))
        password = md5.hexdigest()

        expire_time = time.time() + 60

        if not UserModel.objects.filter(username=username, password=password, salt=salt):
            return JsonResponse(responses.RESPONSE_INVALID_USERNAME_OR_PASSWORD)

        token = str(uuid.uuid1())

        user_status = UserStatus(
            token=token, username=username, expire_time=expire_time)
        user_status.save()
        return JsonResponse(
            {'code': responses.CODE_SUCCESS,
             'data': {'token': token, 'username': username}}
        )


class UserSignUp(View):
    """signup api"""
    def get(self, request):
        """get request"""
        form = request.GET
        return self.handle_sign_up(form)

    def post(self, request):
        """post request"""
        form = request.POST
        return self.handle_sign_up(form)

    @staticmethod
    def handle_sign_up(form):
        """signup api"""
        if not set(['username', 'password']) <= set(form.keys()):
            return JsonResponse(responses.RESPONSE_INVALID_FORM)

        username = form['username']
        password = form['password']

        if UserModel.objects.filter(username=username):
            return JsonResponse(responses.RESPONSE_USERNAME_ALREADY_EXISTS)

        salt = str(uuid.uuid1())

        md5 = hashlib.md5()
        md5.update((password + salt).encode('utf-8'))
        password = md5.hexdigest()

        user = UserModel(username=username, password=password, salt=salt)
        user.save()
        return JsonResponse(responses.RESPONSE_SUCCESS)


class UserInfo(View):
    """get user info"""
    def get(self, request):
        """get request"""
        form = request.GET
        return self.handle_user_info(form)

    def post(self, request):
        """post request"""
        form = request.POST
        return self.handle_user_info(form)

    @staticmethod
    def handle_user_info(form):
        """user info api"""
        if 'token' not in form:
            return JsonResponse(responses.RESPONSE_INVALID_FORM)

        token = form['token']
        user_info = UserStatus.objects.filter(token=token)

        if not user_info:
            return JsonResponse(responses.RESPONSE_INVALID_TOKEN)

        return JsonResponse({'data': {
            'username': user_info[0].username,
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif'
        }, 'code': responses.CODE_SUCCESS})


class UserLogout(View):
    """logout api"""
    def get(self, request):
        """get request"""
        form = request.GET
        return self.handle_logout(form)

    def post(self, request):
        """post request"""
        form = request.POST
        return self.handle_logout(form)

    @staticmethod
    def handle_logout(form):
        """logout api"""
        if 'token' not in form:
            return JsonResponse(responses.RESPONSE_INVALID_FORM)

        token = form['token']
        user_status = UserStatus.objects.filter(token=token)

        if not user_status:
            return JsonResponse(responses.RESPONSE_INVALID_TOKEN)

        user_status.delete()
        return JsonResponse(responses.RESPONSE_SUCCESS)
