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
        url: '/registry/' + repo + '/',
        method: 'get'
    });
}

export function uploadImage(query) {
    return filerequest({
        url: '/registry/upload/',
        method: 'post',
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        data: query
    });
}

export function deleteImage(repo, tag) {
    console.log('/registry/' + repo + '/' + tag + '/');
    return request({
        url: '/registry/' + repo + '/' + tag + '/',
        method: 'delete'
    });
}

export function getFileList(query) {
    return request({
        url: '/registry/history/',
        method: 'get',
        params: query
    });
}
