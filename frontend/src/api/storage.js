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
        params: query
    });
}
