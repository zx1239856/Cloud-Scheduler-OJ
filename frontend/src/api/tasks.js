import request from '@/utils/request';

export function createTask(data) {
    return request({
        url: '/task_settings/',
        method: 'post',
        data
    });
}

export function getTaskList() {
    return request({
        url: '/task_settings/',
        method: 'get'
    });
}

export function updateTask(uuid, data) {
    return request({
        url: '/task_settings/' + uuid + '/',
        method: 'put',
        data
    });
}
