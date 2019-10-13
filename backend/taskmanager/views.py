"""View handlers for TaskManager"""
import logging
import json
from uuid import uuid1
from django.http import JsonResponse
from django.views import View
from django.db.utils import IntegrityError
from django.core.paginator import Paginator
from api.common import RESPONSE
from .models import TaskSettings

LOGGER = logging.getLogger(__name__)


def getUUID():
    return uuid1()


class TaskSettingsHandler(View):
    http_method_names = ['get', 'post', 'put', 'delete']  # specify allowed methods

    def get(self, request):
        """
        @api {get} /task_settings/ Get task settings
        @apiName GetTaskSettings
        @apiGroup TaskSettings
        @apiVersion 0.1.0
        @apiPermission admin

        @apiParam {String} [list_all] When present, will list all task settings
        @apiParam {String} [order_by] Use with list_all, specifies order criteria, available options:
        create_time, name. Use '-' sign to indicate reverse order.
        @apiParam {String} [page] Use with list_all, specifies the page number (starting from 1, per page 25 elements)
        @apiParam {String} [uuid] UUID of the task, do not use together with list_all
        @apiParam {String} [name] Name of the task, do not use together with list_all
        @apiSuccess {Object} payload Response object
        @apiSuccess {Number} payload.page_count Page count
        @apiSuccess {Number} payload.count Total element count
        @apiSuccess {Object[]} payload.entry List of TaskSettings Object
        @apiSuccess {String} payload.entry.uuid Task uuid
        @apiSuccess {String} payload.entry.name Task name
        @apiSuccess {Number} payload.entry.concurrency Task concurrency
        @apiSuccess {Object} payload.entry.task_config Detailed task config
        @apiSuccess {String} payload.entry.create_time Create time of task settings
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """
        response = None
        try:
            params = request.GET
            uuid = params.get('uuid', None)
            name = params.get('name', None)
            list_all = params.get('list_all', None)
            if list_all is not None:
                if uuid is not None or name is not None:
                    response = RESPONSE.INVALID_REQUEST
                else:
                    response = RESPONSE.SUCCESS
                    payload = {}
                    order_by = params.get('order_by', 'id').split(',')
                    page = params.get('page', '1')
                    try:
                        page = int(page)
                        all_pages = Paginator(TaskSettings.objects.filter().order_by(*order_by), 25)
                        curr_page = all_pages.page(page)
                        payload['count'] = all_pages.count
                        payload['page_count'] = all_pages.num_pages if all_pages.count > 0 else 0
                        payload['entry'] = []
                        for item in curr_page.object_list:
                            payload['entry'].append({'uuid': item.uuid, 'name': item.name,
                                                     'concurrency': item.concurrency, 'task_config': item.task_config,
                                                     'create_time': item.create_time})
                        response['payload'] = payload
                    except ValueError:
                        response = RESPONSE.INVALID_REQUEST
            elif uuid is not None or name is not None:
                response = RESPONSE.SUCCESS
                payload = {}
                try:
                    query_dict = {}
                    if uuid is not None:
                        query_dict['uuid'] = uuid
                    if name is not None:
                        query_dict['name'] = name
                    item = TaskSettings.objects.get(**query_dict)
                    payload['page_count'] = payload['count'] = 1
                    payload['entry'] = [{'uuid': item.uuid, 'name': item.name,
                                         'concurrency': item.concurrency, 'task_config': item.task_config,
                                         'create_time': item.create_time}]
                except TaskSettings.DoesNotExist:
                    payload['page_count'] = 0
                    payload['count'] = 0
                    payload['entry'] = []
                finally:
                    response['payload'] = payload
            else:
                response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)

    def post(self, request):
        """
        @api {post} /task_settings/ Update task settings
        @apiName UpdateTaskSettings
        @apiGroup TaskSettings
        @apiVersion 0.1.0
        @apiPermission admin
        @apiDescription Leave optional params empty to keep them as the original value
        @apiParamExample {json} Request-Example:
        {
            "uuid": "123456",
            "concurrency": 3
        }
        @apiParam {String} uuid UUID of the task
        @apiParam {String} [name] Name of the task
        @apiParam {Number} [concurrency] Number of concurrent works of the task
        @apiParam {Object} [task_config] Task configuration
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """
        response = None
        try:
            response = RESPONSE.SUCCESS
            query = json.loads(request.body)
            if 'uuid' not in query.keys():
                response = RESPONSE.INVALID_REQUEST
            else:
                try:
                    item = TaskSettings.objects.get(uuid=query['uuid'])
                    if 'name' in query.keys():
                        item.name = str(query['name'])
                    if 'concurrency' in query.keys():
                        item.concurrency = int(query['concurrency'])
                    if 'task_config' in query.keys():
                        item.task_config = dict(query['task_config'])
                    item.save(force_update=True)
                except ValueError:
                    response = RESPONSE.INVALID_REQUEST
                except TaskSettings.DoesNotExist:
                    response = RESPONSE.OPERATION_FAILED
                    response['message'] += " {}".format("Object does not exist.")
        except json.decoder.JSONDecodeError:
            response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)

    def delete(self, request):
        """
        @api {delete} /task_settings/ Delete task settings
        @apiName DeleteTaskSettings
        @apiGroup TaskSettings
        @apiVersion 0.1.0
        @apiPermission admin
        @apiDescription When uuid and name are both provided, we try to match them both
        @apiParamExample {json} Request-Example:
        {
            "uuid": "123456"
        }
        @apiParam {String} [uuid] UUID of the task
        @apiParam {String} [name] Name of the task
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """
        response = None
        try:
            query = json.loads(request.body)
            query_dict = {}
            if 'name' in query.keys():
                query_dict['name'] = query['name']
            if 'uuid' in query.keys():
                query_dict['uuid'] = query['uuid']
            try:
                TaskSettings.objects.get(**query_dict).delete()
                response = RESPONSE.SUCCESS
            except TaskSettings.DoesNotExist:
                response = RESPONSE.OPERATION_FAILED
            if not query_dict:
                response = RESPONSE.INVALID_REQUEST
        except json.decoder.JSONDecodeError:
            response = RESPONSE.INVALID_REQUEST
        finally:
            return JsonResponse(response)

    def put(self, request):
        """
        @api {put} /task_settings/ Create task settings
        @apiName CreateTaskSettings
        @apiGroup TaskSettings
        @apiVersion 0.1.0
        @apiPermission admin
        @apiParamExample {json} Request-Example:
        {
            "name": "123456",
            "concurrency": 3,
            "task_config": {}
        }
        @apiParam {String} name Name of the task
        @apiParam {Number} concurrency Number of concurrent works of the task
        @apiParam {Object} task_config Task configuration
        @apiSuccess {Object} payload Success payload is empty
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse OperationFailed
        @apiUse Unauthorized
        @apiUse PermissionDenied
        """
        response = None
        try:
            query = json.loads(request.body)
            if 'name' not in query.keys() or 'concurrency' not in query.keys() or 'task_config' not in query.keys():
                response = RESPONSE.INVALID_REQUEST
            else:
                try:
                    TaskSettings.objects.create(uuid=str(getUUID()), name=query['name'], concurrency=query['concurrency'],
                                                task_config=query['task_config'])
                    response = RESPONSE.SUCCESS
                except IntegrityError as ex:
                    LOGGER.warning(ex)
                    response = RESPONSE.OPERATION_FAILED
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)
