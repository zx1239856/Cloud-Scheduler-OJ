import request from '@/utils/request';

export function getOAuthApp(page) {
    return request({
        url: '/oauth/applications/?page=' + page,
        method: 'get'
    });
}

export function getOAuthAppDetail(uuid) {
    return request({
        url: '/oauth/applications/' + uuid + '/',
        method: 'get'
    });
}

export function createOAuthApp(name, redirect_uris) {
    return request({
        url: '/oauth/applications/',
        method: 'post',
        data: {
            name: name,
            redirect_uris: redirect_uris,
            shared: true
        }
    });
}

export function updateOAuthApp(uuid, name, redirect_uris) {
    return request({
        url: '/oauth/applications/' + uuid + '/',
        method: 'put',
        data: {
            name: name,
            redirect_uris: redirect_uris,
            shared: true
        }
    });
}

export function deleteOAuthApp(uuid) {
    return request({
        url: '/oauth/applications/' + uuid + '/',
        method: 'delete'
    });
}
