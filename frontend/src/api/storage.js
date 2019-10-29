import request from '@/utils/request';

export function getFileList(query) {
    return request({
        url: '/storage/upload_file/',
        method: 'get',
        params: query
    });
}

export function uploadFile(query) {
    return request({
        url: '/storage/upload_file/',
        method: 'post',
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        data: query,
        withCredentials: true
    });
}

export function reuploadFile(query) {
    return request({
        url: '/storage/upload_file/',
        method: 'put'
    });
}

export function getPVCList(query) {
    return request({
        url: '/storage/',
        method: 'get',
        params: query
    });
}

export function createPVC(query) {
    return request({
        url: '/storage/',
        method: 'post',
        data: query
    });
}

export function deletePVC(query) {
    return request({
        url: '/storage/',
        method: 'delete',
        data: query
    });
}
