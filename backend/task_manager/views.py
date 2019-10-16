"""View handlers for TaskManager"""
import logging
import json
from uuid import uuid1
from django.http import JsonResponse
from django.views import View
from django.db.utils import IntegrityError
from django.core.paginator import Paginator
from api.common import RESPONSE
from user_model.models import UserType
from .models import TaskSettings, Task, TASK

LOGGER = logging.getLogger(__name__)


def getUUID():
    return uuid1()


class TaskSettingsListHandler(View):
    http_method_names = ['get', 'post']

    def get(self, request, **kwargs):
        """
        @api {get} /task_settings/ Get task settings list
        @apiName GetTaskSettingsList
        @apiGroup TaskSettings
        @apiVersion 0.1.0
        @apiPermission user

        @apiParam {String} [order_by] Specifies list order criteria, available options:
        create_time, name. Use '-' sign to indicate reverse order.
        @apiParam {String} [page] Specifies the page number (starting from 1, per page 25 elements)
        @apiSuccess {Object} payload Response object
        @apiSuccess {Number} payload.page_count Page count
        @apiSuccess {Number} payload.count Total element count
        @apiSuccess {Object[]} payload.entry List of TaskSettings Object
        @apiSuccess {String} payload.entry.uuid Task uuid
        @apiSuccess {String} payload.entry.name Task name
        @apiSuccess {Number} [payload.entry.concurrency] Task concurrency (admin only)
        @apiSuccess {Object} [payload.entry.task_config] Detailed task config (admin only)
        @apiSuccess {String} payload.entry.create_time Create time of task settings
        @apiUse APIHeader
        @apiUse Success
        @apiUse ServerError
        @apiUse InvalidRequest
        @apiUse Unauthorized
        """
        response = RESPONSE.SUCCESS
        try:
            user = kwargs.get('__user', None)
            if user is None:
                raise Exception("Internal exception raised when trying to get `User` object.")
            params = request.GET
            payload = {}
            order_by = params.get('order_by', 'id').split(',')
            page = params.get('page', '1')
            page = int(page)
            all_pages = Paginator(TaskSettings.objects.filter().order_by(*order_by), 25)
            curr_page = all_pages.page(page)
            payload['count'] = all_pages.count
            payload['page_count'] = all_pages.num_pages if all_pages.count > 0 else 0
            payload['entry'] = []
            for item in curr_page.object_list:
                entry = {'uuid': item.uuid, 'name': item.name, 'create_time': item.create_time}
                if user.user_type == UserType.ADMIN:
                    entry['concurrency'] = item.concurrency
                    entry['task_config'] = item.task_config
                payload['entry'].append(entry)
            response['payload'] = payload
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)

    def post(self, request, **kwargs):
        """
        @api {post} /task_settings/ Create task settings
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
            user = kwargs.get('__user', None)
            if user is None:
                raise Exception("Internal exception raised when trying to get `User` object.")
            elif user.user_type == UserType.USER:
                response = RESPONSE.PERMISSION_DENIED
            else:
                query = json.loads(request.body)
                if 'name' not in query.keys() or 'concurrency' not in query.keys() or 'task_config' not in query.keys():
                    response = RESPONSE.INVALID_REQUEST
                else:
                    TaskSettings.objects.create(uuid=str(getUUID()), name=query['name'],
                                                concurrency=query['concurrency'],
                                                task_config=query['task_config'])
                    response = RESPONSE.SUCCESS
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except IntegrityError as ex:
            LOGGER.warning(ex)
            response = RESPONSE.OPERATION_FAILED
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)


class TaskSettingsItemHandler(View):
    http_method_names = ['get', 'put', 'delete']  # specify allowed methods

    def get(self, _, **kwargs):
        """
        @api {get} /task_settings/<string:uuid>/ Get detailed task settings
        @apiName GetTaskSettings
        @apiGroup TaskSettings
        @apiVersion 0.1.0
        @apiPermission admin

        @apiSuccess {Object} payload Response object
        @apiSuccess {String} payload.uuid Task uuid
        @apiSuccess {String} payload.name Task name
        @apiSuccess {Number} payload.concurrency Task concurrency
        @apiSuccess {Object} payload.task_config Detailed task config
        @apiSuccess {String} payload.create_time Create time of task settings
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
            uuid = kwargs.get('uuid', None)
            assert uuid is not None
            response = RESPONSE.SUCCESS
            item = TaskSettings.objects.get(uuid=uuid)
            response['payload'] = {'uuid': item.uuid, 'name': item.name, 'concurrency': item.concurrency,
                                   'task_config': item.task_config, 'create_time': item.create_time}
        except TaskSettings.DoesNotExist:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " {}".format("Object does not exist.")
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)

    def put(self, request, **kwargs):
        """
        @api {put} /task_settings/<string:uuid>/ Update task settings
        @apiName UpdateTaskSettings
        @apiGroup TaskSettings
        @apiVersion 0.1.0
        @apiPermission admin
        @apiDescription Leave optional params empty to keep them as the original value
        @apiParamExample {json} Request-Example:
        {
            "concurrency": 3
        }
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
            uuid = kwargs.get('uuid', None)
            assert uuid is not None
            query = json.loads(request.body)
            response = RESPONSE.SUCCESS
            item = TaskSettings.objects.get(uuid=uuid)
            if 'name' in query.keys():
                item.name = str(query['name'])
            if 'concurrency' in query.keys():
                item.concurrency = int(query['concurrency'])
            if 'task_config' in query.keys():
                item.task_config = dict(query['task_config'])
            item.save(force_update=True)
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except IntegrityError:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " {}".format("Name duplicates.")
        except TaskSettings.DoesNotExist:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " {}".format("Object does not exist.")
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)

    def delete(self, _, **kwargs):
        """
        @api {delete} /task_settings/<string:uuid>/ Delete task settings
        @apiName DeleteTaskSettings
        @apiGroup TaskSettings
        @apiVersion 0.1.0
        @apiPermission admin
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
            uuid = kwargs.get('uuid', None)
            assert uuid is not None
            TaskSettings.objects.get(uuid=uuid).delete()
            response = RESPONSE.SUCCESS
        except TaskSettings.DoesNotExist:
            response = RESPONSE.OPERATION_FAILED
        finally:
            return JsonResponse(response)


class ConcreteTaskListHandler(View):
    http_method_names = ['get', 'post']

    def get(self, request, **kwargs):
        response = RESPONSE.SUCCESS
        try:
            user = kwargs.get('__user', None)
            if user is None:
                raise Exception("Internal exception raised when trying to get `User` object.")
            page = request.GET.get('page', '1')
            page = int(page)
            filter_dict = {}
            if user.user_type == UserType.USER:
                filter_dict['user'] = user
            all_pages = Paginator(Task.objects.filter(**filter_dict).order_by("-create_time", "status"), 25)
            curr_page = all_pages.page(page)
            payload = {'count': all_pages.count, 'page_count': all_pages.num_pages if all_pages.count > 0 else 0,
                       'entry': []}
            for item in curr_page.object_list:
                payload['entry'].append({'settings': {'name': item.settings.name, 'uuid': item.settings.uuid},
                                         'status': item.status,
                                         'uuid': item.uuid,
                                         'user': item.user.username,
                                         'create_time': item.create_time})
            response['payload'] = payload
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)

    def post(self, request, **kwargs):
        response = None
        try:
            user = kwargs.get('__user', None)
            if user is None:
                raise Exception("Internal exception raised when trying to get `User` object.")
            else:
                query = json.loads(request.body)
                if 'settings_uuid' not in query.keys():
                    response = RESPONSE.INVALID_REQUEST
                else:
                    settings = TaskSettings.objects.get(uuid=query['settings_uuid'])
                    item = Task.objects.create(user=user, settings=settings, uuid=str(getUUID()))
                    response = RESPONSE.SUCCESS
                    response['payload'] = {'settings': {'name': item.settings.name, 'uuid': item.settings.uuid},
                                           'status': item.status,
                                           'uuid': item.uuid,
                                           'user': item.user.username,
                                           'create_time': item.create_time}
        except TaskSettings.DoesNotExist:
            response = RESPONSE.OPERATION_FAILED
            response["message"] += " Failed to find corresponding task settings."
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except IntegrityError as ex:
            LOGGER.warning(ex)
            response = RESPONSE.OPERATION_FAILED
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)


class ConcreteTaskHandler(View):
    http_method_names = ['get', 'delete']

    @staticmethod
    def _get_task(arg_dict):
        user = arg_dict.get('__user', None)
        if user is None:
            raise Exception("Internal exception raised when trying to get `User` object.")
        uuid = arg_dict.get('uuid', None)
        if uuid is None:
            return None
        else:
            item = Task.objects.get(uuid=uuid, user=user)
            return item

    def get(self, _, **kwargs):
        response = RESPONSE.SUCCESS
        try:
            item = self._get_task(kwargs)
            if item is None:
                response = RESPONSE.INVALID_REQUEST
            else:
                response['payload'] = {'settings': {'name': item.settings.name, 'uuid': item.settings.uuid},
                                       'status': item.status,
                                       'uuid': item.uuid,
                                       'user': item.user.username,
                                       'log': item.logs,
                                       'create_time': item.create_time}
        except Task.DoesNotExist:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " Object does not exist."
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)

    def delete(self, _, **kwargs):
        response = RESPONSE.SUCCESS
        try:
            item = self._get_task(kwargs)
            if item is None:
                response = RESPONSE.INVALID_REQUEST
            else:
                item.status = TASK.DELETING  # schedule canceling by changing status
                item.save(force_update=True)
        except Task.DoesNotExist:
            response = RESPONSE.OPERATION_FAILED
            response['message'] += " Object does not exist."
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)
