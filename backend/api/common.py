"""Common variable used in modules"""
import random
import string
from uuid import uuid1
from kubernetes.client import Configuration, ApiClient
from config import KUBERNETES_CLUSTER_TOKEN, KUBERNETES_API_SERVER_URL

"""
@apiDefine admin Admin access only
Only admin user can access this API
"""
"""
@apiDefine user User access only
All users can access this API
"""
"""
@apiDefine super_admin Super Admin access only
Only super admin can access this API
"""
"""
@apiDefine APIHeader
@apiHeader {String} X-Access-Token access token of the user
@apiHeader {String} X-Access-Username username
"""

USERSPACE_NAME = 'cloud-scheduler-userspace'
OAUTH_LOGIN_URL = 'oauth/login/'


def get_uuid():
    return uuid1()


def random_password(length=32):
    password_chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_chars) for _ in range(length))


def get_kubernetes_api_client():
    conf = Configuration()
    conf.host = KUBERNETES_API_SERVER_URL
    conf.verify_ssl = False
    conf.api_key = {"authorization": "Bearer " + KUBERNETES_CLUSTER_TOKEN}
    return ApiClient(conf)


class _Response(object):
    @property
    def SUCCESS(self):
        """
        @apiDefine Success
        @apiSuccessExample {json} Success-Response:
        HTTP/1.1 200 OK
        {
            "status": 200,
            "message": "",
            "payload": {}
        }
        """
        return {
            "status": 200,
            "message": "",
            "payload": {},
        }

    @property
    def SERVER_ERROR(self):
        """
        @apiDefine ServerError
        @apiError ServerError Internal server error
        @apiErrorExample {json} Error-Response:
        HTTP/1.1 200 OK
        {
            "status": 500,
            "message": "Internal server error.",
            "payload": {}
        }
        """
        return {
            "status": 500,
            "message": "Internal server error.",
            "payload": {},
        }

    @property
    def NOT_IMPLEMENTED(self):
        """
        @apiDefine NotImplemented
        @apiError NotImplemented Method not implemented
        @apiErrorExample {json} Error-Response:
        HTTP/1.1 200 OK
        {
            "status": 501,
            "message": "Not implemented method.",
            "payload": {}
        }
        """
        return {
            "status": 501,
            "message": "Not implemented method.",
            "payload": {},
        }

    @property
    def INVALID_REQUEST(self):
        """
        @apiDefine InvalidRequest
        @apiError InvalidRequest Request is invalid
        @apiErrorExample {json} Error-Response:
        HTTP/1.1 200 OK
        {
            "status": 400,
            "message": "Invalid request.",
            "payload": {}
        }
        """
        return {
            "status": 400,
            "message": "Invalid request.",
            "payload": {},
        }

    @property
    def OPERATION_FAILED(self):
        """
        @apiDefine OperationFailed
        @apiError OperationFailed Operation is unsuccessful
        @apiErrorExample {json} Error-Response:
        HTTP/1.1 200 OK
        {
            "status": 402,
            "message": "Operation is unsuccessful.",
            "payload": {}
        }
        """
        return {
            "status": 402,
            "message": "Operation is unsuccessful.",
            "payload": {},
        }

    @property
    def UNAUTHORIZED(self):
        """
        @apiDefine Unauthorized
        @apiError Unauthorized User is unauthorized
        @apiErrorExample {json} Error-Response:
        HTTP/1.1 200 OK
        {
            "status": 401,
            "message": "User is unauthorized.",
            "payload": {}
        }
        """
        return {
            "status": 401,
            "message": "User is unauthorized.",
            "payload": {},
        }

    @property
    def PERMISSION_DENIED(self):
        """
        @apiDefine PermissionDenied
        @apiError PermissionDenied User does not have permission to access
        @apiErrorExample {json} Error-Response:
        HTTP/1.1 200 OK
        {
            "status": 403,
            "message": "Permission denied.",
            "payload": {}
        }
        """
        return {
            "status": 403,
            "message": "Permission denied.",
            "payload": {},
        }

    @property
    def RESOURCE_LOCKED(self):
        """
        @apiDefine PermissionDenied
        @apiError PermissionDenied User does not have permission to access
        @apiErrorExample {json} Error-Response:
        HTTP/1.1 200 OK
        {
            "status": 423,
            "message": "The requested resource is unavailable.",
            "payload": {}
        }
        """
        return {
            "status": 423,
            "message": "The requested resource is unavailable.",
            "payload": {},
        }

    @property
    def NOT_FOUND(self):
        """
        @apiDefine PermissionDenied
        @apiError PermissionDenied User does not have permission to access
        @apiErrorExample {json} Error-Response:
        HTTP/1.1 200 OK
        {
            "status": 404,
            "message": "The requested resource is not found.",
            "payload": {}
        }
        """
        return {
            "status": 404,
            "message": "The requested resource is not found.",
            "payload": {},
        }


RESPONSE = _Response()
