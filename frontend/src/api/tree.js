import request from '@/utils/request';

export function getTree(query) {
    return request({
        url: '/tree/',
        method: 'get',
        params: query
    });
}

export function getFile(path, filename) {
    return request({
        url: '/tree/file/' + path + '/' + filename + '/',
        method: 'get'
    });
}

export function createFile(path, filename, data) {
    return request({
        url: '/tree/file/' + path + '/' + filename + '/',
        method: 'post',
        data
    });
}

export function updateFile(path, filename, data) {
    return request({
        url: '/tree/file/' + path + '/' + filename + '/',
        method: 'put',
        data
    });
}

export function deleteFile(path, filename) {
    return request({
        url: '/tree/file/' + path + '/' + filename + '/',
        method: 'delete'
    });
}

export function addDirectory(path, directoryname) {
    return request({
        url: '/tree/directory/' + path + '/' + directoryname + '/',
        method: 'post'
    });
}

export function deleteDirectory(path, directoryname) {
    return request({
        url: '/tree/directory/' + path + '/' + directoryname + '/',
        method: 'delete'
    });
}
