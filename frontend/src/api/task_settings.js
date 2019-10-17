import request from '@/utils/request';

export function createTaskSettings(data) {
    return request({
        url: '/task_settings/',
        method: 'post',
        data
    });
}

export function getTaskSettingsList() {
    return request({
        url: '/task_settings/',
        method: 'get'
    });
}

export function updateTaskSettings(uuid, data) {
    return request({
        url: '/task_settings/' + uuid + '/',
        method: 'put',
        data
    });
}

export function deleteTaskSettings(uuid) {
    return request({
        url: '/task_settings/' + uuid + '/',
        method: 'delete'
    });
}
