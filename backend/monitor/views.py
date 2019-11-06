import logging
from django.http import JsonResponse
from django.views import View
from kubernetes.client import CoreV1Api
from api.common import RESPONSE, get_kubernetes_api_client

LOGGER = logging.getLogger(__name__)


class PodListHandler(View):
    http_method_names = ['get']

    def get(self, request, **_):
        response = RESPONSE.SUCCESS
        try:
            params = request.GET
            page = params.get('page', '1')
            page = int(page)
            api = CoreV1Api(get_kubernetes_api_client())
            ret = api.list_pod_for_all_namespaces(watch=False)
            response['payload'] = {
                'count': len(ret.items),
                'page_count': (len(ret.items) + 24) // 25,
                'entry': []
            }
            if page < 1 or page > response['payload']['page_count']:
                raise ValueError()
            for i in ret.items[25 * (page - 1): 25 * page]:
                response['payload']['entry'].append({
                    'pod_ip': i.status.pod_ip,
                    'namespace': i.metadata.namespace,
                    'name': i.metadata.name,
                    'create_time': i.metadata.creation_timestamp,
                    'uid': i.metadata.uid,
                    'status': i.status.phase if not i.metadata.deletion_timestamp else 'Terminating',
                    'node_name': i.spec.node_name,
                })
        except ValueError:
            response = RESPONSE.INVALID_REQUEST
        except Exception as ex:
            LOGGER.error(ex)
            response = RESPONSE.SERVER_ERROR
        finally:
            return JsonResponse(response)
