"""Common variable used in modules"""

"""
@apiDefine admin User access only
Only admin user can access this API
"""
"""
@apiDefine user User access only
All users can access this API
"""


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
            "message": "Internal server error",
            "payload": {}
        }
        """
        return {
            "status": 500,
            "message": "Internal server error",
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
            "message": "Not implemented method",
            "payload": {}
        }
        """
        return {
            "status": 501,
            "message": "Not implemented method",
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
            "message": "Invalid request",
            "payload": {}
        }
        """
        return {
            "status": 400,
            "message": "Invalid request",
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
            "message": "User is unauthorized",
            "payload": {}
        }
        """
        return {
            "status": 401,
            "message": "User is unauthorized",
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
            "message": "Permission denied",
            "payload": {}
        }
        """
        return {
            "status": 403,
            "message": "Permission denied",
            "payload": {},
        }


RESPONSE = _Response()
