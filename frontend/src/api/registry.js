import request from '@/utils/request';
import filerequest from '@/utils/file-request';

export function getRepositories(query) {
    return request({
        url: '/registry/',
        method: 'get'
    });
}

export function getRepository(repo) {
    return request({
        url: '/registry/repository/' + repo + '/',
        method: 'get'
    });
}

export function uploadImage(param) {
    return filerequest({
        url: '/registry/repository/upload/',
        method: 'post',
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        data: param
    });
}

export function deleteImage(repo, tag) {
    return request({
        url: '/registry/repository/' + repo + '/' + tag + '/',
        method: 'delete'
    });
}

export function getImageList(query) {
    return request({
        url: '/registry/history/',
        method: 'get',
        params: query
    });
}
