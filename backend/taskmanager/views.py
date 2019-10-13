"""View handlers for TaskManager"""
import logging
from django.http import JsonResponse
from django.views import View
from api.common import RESPONSE
# from .models import TaskSettings, Task, TASK

LOGGER = logging.getLogger(__name__)


class TaskSettingsHandler(View):
    http_method_names = ['get', 'post', 'delete']  # specify allowed methods

    def get(self, request):
        """
        @api {get} /task_settings/ Get task settings
        @apiName GetTaskSettings
        @apiGroup TaskSettings
        @apiVersion 0.1.0
        @apiPermission admin

        @apiParam {String} list_all When present, will list all task settings
        @apiParam {String} uuid UUID of the task, do not use together with list_all
        @apiSuccess {Object} payload Response info
        @apiSuccess {Object} payload.info Task info
        @apiUse Success
        @apiUse ServerError
        @apiUse NotImplemented
        @apiUse InvalidRequest
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """
        response = None
        try:
            params = request.GET
            uuid = params.get('uuid', None)
            LOGGER.info(params)
            list_all = params.get('list_all', None)
            if list_all is not None:
                response = RESPONSE.SUCCESS
                response['payload'] = {'req': 'list_all'}
            elif uuid is not None:
                response = RESPONSE.SUCCESS
                response['payload'] = {'req': uuid}
            else:
                response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)

    def post(self, request):
        return JsonResponse(RESPONSE.SUCCESS)

    def delete(self, request):
        return JsonResponse(RESPONSE.SUCCESS)
