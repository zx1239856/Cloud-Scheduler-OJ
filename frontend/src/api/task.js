import request from '@/utils/request';

export function getTaskList(page) {
    return request({
        url: '/task/',
        method: 'get',
        params: { page: page }
    });
}

export function createTask(settings_uuid) {
    return request({
        url: '/task/',
        method: 'post',
        data: { settings_uuid }
    });
}

export function deleteTask(task_uuid) {
    return request({
        url: '/task/' + task_uuid + '/',
        method: 'delete'
    });
}

export function getTask(task_uuid) {
    return request({
        url: '/task/' + task_uuid + '/',
        method: 'get'
    });
}
