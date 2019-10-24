import request from '@/utils/request';

export function getPodList(query) {
    return request({
        url: '/pods/',
        method: 'get',
        params: query
    });
}
