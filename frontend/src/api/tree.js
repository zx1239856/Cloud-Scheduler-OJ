import request from '@/utils/request';

export function getTreePath(settings_uuid, path) {
    return request({
        url: '/user_space/' + settings_uuid + '/',
        method: 'get',
        params: { path: path }
    });
}

export function getFile(settings_uuid, file) {
    return request({
        url: '/user_space/' + settings_uuid + '/',
        method: 'get',
        params: { file: file }
    });
}

export function createFile(path, filename, data) {
    return request({
        url: '/tree/file/' + path + '/' + filename + '/',
        method: 'post',
        data
    });
}

export function updateFile(settings_uuid, filename, content) {
    return request({
        url: '/user_space/' + settings_uuid + '/',
        method: 'put',
        data: {
            file: filename,
            old_file: filename,
            content: content
        }
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
