import request from '@/utils/request';

export default function getVNCPod(settings_uuid) {
    return request({
        url: '/vnc/' + settings_uuid + '/',
        method: 'get'
    });
}
