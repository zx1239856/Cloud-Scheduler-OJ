"""
API for user module
"""
import hashlib
import time
import uuid
import json
import logging
from functools import wraps
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError
from user_model.models import UserModel, UserType
from task_manager.views import get_uuid
from api.common import RESPONSE
from config import USER_TOKEN_EXPIRE_TIME

LOGGER = logging.getLogger(__name__)


def user_passes_test(test_func):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            ret = test_func(request)
            if ret == 1:
                return JsonResponse(RESPONSE.UNAUTHORIZED)
            elif ret == -1:
                return JsonResponse(RESPONSE.PERMISSION_DENIED)
            else:
                kwargs['__user'] = ret
                return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def login_required(function=None):
    """
    Decorator for views that checks that the user is logged in
    """

    def test_login(request):
        if 'HTTP_X_ACCESS_TOKEN' in request.META.keys() and 'HTTP_X_ACCESS_USERNAME' in request.META.keys():
            try:
                username = request.META['HTTP_X_ACCESS_USERNAME']
                header_token = request.META['HTTP_X_ACCESS_TOKEN']
                user = UserModel.objects.get(username=username)
                token = TokenManager.get_token(user)
                if token == header_token:
                    TokenManager.update_token(user)
                    return user
                else:
                    return 1
            except Exception as ex:
                LOGGER.warning(ex)
                return 1
        else:
            return 1

    actual_decorator = user_passes_test(test_login)
    if function:
        return actual_decorator(function)
    return actual_decorator


def permission_required(function=None):
    """
    Decorator for views that checks that the user is logged in
    """

    def test_permission(request):
        if 'HTTP_X_ACCESS_TOKEN' in request.META.keys() and 'HTTP_X_ACCESS_USERNAME' in request.META.keys():
            try:
                username = request.META['HTTP_X_ACCESS_USERNAME']
                header_token = request.META['HTTP_X_ACCESS_TOKEN']
                user = UserModel.objects.get(username=username)
                token = TokenManager.get_token(user)
                if token == header_token:
                    if user.user_type == UserType.ADMIN:
                        TokenManager.update_token(user)
                        return user
                    else:
                        return -1
                else:
                    return 1
            except Exception as ex:
                LOGGER.warning(ex)
                return 1
        else:
            return 1

    actual_decorator = user_passes_test(test_permission)
    if function:
        return actual_decorator(function)
    return actual_decorator


class TokenManager:
    @staticmethod
    def create_token(user):
        token = str(uuid.uuid1())
        user.token = token
        user.token_expire_time = round(time.time()) + USER_TOKEN_EXPIRE_TIME
        try:
            user.save(force_update=True)
        except Exception as ex:
            LOGGER.error(ex)
        return token

    @staticmethod
    def update_token(user):
        user.token_expire_time = round(time.time()) + USER_TOKEN_EXPIRE_TIME
        try:
            user.save(force_update=True)
        except Exception as ex:
            LOGGER.error(ex)

    @staticmethod
    def get_token(user):
        try:
            if user.token_expire_time > time.time():
                return user.token
            else:
                return ''
        except Exception as ex:
            LOGGER.error(ex)


class UserLogin(View):
    """User login view"""

    def post(self, request):
        """
        @api {post} /user/login/ User login
        @apiName UserLogin
        @apiGroup User
        @apiVersion 0.1.0
        @apiPermission user

        @apiParam {String} [username] Specifies the username as the unique identification.
        @apiParam {String} [password] Specifies the password.
        @apiSuccess {Object} payload Response object
        @apiSuccess {String} payload.username Username
        @apiSuccess {String} payload.token Total element count
        @apiSuccess {String} payload.avatar Avatar source of user.
        @apiParamExample {json} Request-Example:
        {
            "username": "123456",
            "password": "123456"
        }
        @apiUse Success
        @apiUse OperationFailed
        @apiUse InvalidRequest
        @apiUse ServerError
        """
        response = None
        try:
            request = json.loads(request.body)
            username = request.get('username', None)
            password = request.get('password', None)
            if username is None or password is None:
                raise ValueError()
            user = UserModel.objects.get(username=username)
            salt = user.salt
            md5 = hashlib.md5()
            md5.update((password + salt).encode('utf-8'))
            password = md5.hexdigest()
            md5 = hashlib.md5()
            md5.update(user.email.encode('utf-8'))
            if password == user.password:
                token = TokenManager.create_token(user)
                response = RESPONSE.SUCCESS
                response['payload'] = {
                    'username': user.username,
                    'uuid': user.uuid,
                    'token': token,
                    'avatar': 'https://fdn.geekzu.org/avatar/{}'.format(md5.hexdigest()),
                    'permission': 'admin' if user.user_type else 'user'
                }
            else:
                raise UserModel.DoesNotExist()
        except UserModel.DoesNotExist:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " {}".format("Invalid username or password.")
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)


class UserHandler(View):
    http_method_names = ['get', 'put', 'delete', 'post']

    @method_decorator(login_required)
    def get(self, _, **kwargs):
        """
        @api {get} /user/ Get user info.
        @apiName GetUserInfo
        @apiGroup User
        @apiVersion 0.1.0
        @apiPermission user

        @apiSuccess {Object} payload Response object
        @apiSuccess {String} payload.username Username
        @apiSuccess {String} payload.token Total element count
        @apiSuccess {String} payload.avatar Avatar source of user.
        @apiUse APIHeader
        @apiUse Success
        @apiUse InvalidRequest
        """
        user = kwargs.get('__user', None)
        if user is not None:
            response = RESPONSE.SUCCESS
            response['payload'] = {
                'username': user.username,
                'email': user.email,
                'create_time': user.create_time,
                'uuid': user.uuid,
            }
            return JsonResponse(response)
        else:
            return JsonResponse(RESPONSE.INVALID_REQUEST)

    def post(self, request):
        """
        @api {post} /user/ User Sign Up
        @apiName UserSignUp
        @apiGroup User
        @apiVersion 0.1.0
        @apiPermission user

        @apiParam {String} [username] Specifies the username as the unique identification.
        @apiParam {String} [password] Specifies the password.
        @apiParam {String} [email] Specifies the email.
        @apiParamExample {json} Request-Example:
        {
            "username": "123456",
            "password": "123456",
            "email": "abc@163.com"
        }
        @apiUse Success
        @apiUse OperationFailed
        @apiUse InvalidRequest
        @apiUse ServerError
        """
        response = None
        try:
            request = json.loads(request.body)
            username = request.get('username', None)
            password = request.get('password', None)
            email = request.get('email', None)
            if username is None or password is None or email is None:
                raise ValueError()
            else:
                salt = str(uuid.uuid1())
                md5 = hashlib.md5()
                md5.update((password + salt).encode('utf-8'))
                password = md5.hexdigest()
                user = UserModel(uuid=str(get_uuid()), username=username, password=password, salt=salt, email=email)
                user.save()
                response = RESPONSE.SUCCESS
        except IntegrityError:
            response = RESPONSE.OPERATION_FAILED
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)

    @method_decorator(login_required)
    def delete(self, _, **kwargs):
        """
        @api {delete} /user/ Delete user.
        @apiName UserDelete
        @apiGroup User
        @apiVersion 0.1.0
        @apiPermission user

        @apiUse APIHeader
        @apiUse Success
        @apiUse OperationFailed
        @apiUse InvalidRequest
        """
        user = kwargs.get('__user', None)
        if user is not None:
            try:
                user.delete()
                return JsonResponse(RESPONSE.SUCCESS)
            except Exception as ex:
                LOGGER.error(ex)
                return JsonResponse(RESPONSE.OPERATION_FAILED)
        else:
            return JsonResponse(RESPONSE.INVALID_REQUEST)

    @method_decorator(login_required)
    def put(self, request, **kwargs):
        """
        @api {put} /user/ Update User Info
        @apiName UserUpdate
        @apiGroup User
        @apiVersion 0.1.0
        @apiPermission user

        @apiParam {String} [email] Specifies new email.
        @apiParam {String} [password] Specifies new password.
        @apiParamExample {json} Request-Example:
        {
            "email": "abc@163.com",
            "password": "123456"
        }
        @apiUse APIHeader
        @apiUse Success
        @apiUse OperationFailed
        @apiUse InvalidRequest
        @apiUse ServerError
        """
        response = None
        try:
            user = kwargs.get('__user', None)
            request = json.loads(request.body)
            if user is not None:
                response = RESPONSE.SUCCESS
                email = request.get('email', None)
                password = request.get('password', None)
                if email is not None:
                    user.email = email
                if password is not None:
                    md5 = hashlib.md5()
                    md5.update((password + user.salt).encode('utf-8'))
                    password = md5.hexdigest()
                    user.password = password
                user.save(force_update=True)
            else:
                raise ValueError()
        except IntegrityError:
            response = RESPONSE.OPERATION_FAILED
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)


class UserLogout(View):
    """logout api"""

    def get(self, _, **kwargs):
        """
        @api {get} /user/logout/ User logout
        @apiName UserLogout
        @apiGroup User
        @apiVersion 0.1.0
        @apiPermission user

        @apiUse APIHeader
        @apiUse Success
        @apiUse OperationFailed
        @apiUse InvalidRequest
        """
        user = kwargs.get('__user', None)
        if user is not None:
            try:
                user.token = ""
                user.save(force_update=True)
                return JsonResponse(RESPONSE.SUCCESS)
            except Exception as ex:
                LOGGER.error(ex)
                return JsonResponse(RESPONSE.OPERATION_FAILED)
        else:
            return JsonResponse(RESPONSE.INVALID_REQUEST)
