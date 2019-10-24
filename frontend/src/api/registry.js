import request from '@/utils/request';

export function getRepositories(query) {
    return request({
        url: '/registry/',
        method: 'get'
    });
}

export function getRepository(repo) {
    return request({
        url: '/registry/' + repo + '/',
        method: 'get'
    });
}

export function uploadImage(query) {
    return request({
        url: '/registry/upload/',
        method: 'post',
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        data: query
    });
}

export function deleteImage(repo, tag) {
    return request({
        url: '/registry/' + repo + '/delete/' + tag + '/',
        method: 'delete'
    });
}
