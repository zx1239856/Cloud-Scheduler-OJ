import request from '@/utils/request';

export function getAdminList() {
    return request({
        url: '/user/admin/',
        method: 'get'
    });
}

export function createAdmin(username, email) {
    return request({
        url: '/user/admin/',
        method: 'post',
        data: {
            username: username,
            email: email
        }
    });
}

export function updateAdmin(uuid, email, password_reset) {
    return request({
        url: '/user/admin/' + uuid + '/',
        method: 'put',
        data: {
            email: email,
            password_reset: password_reset
        }
    });
}

export function deleteAdmin(uuid) {
    return request({
        url: '/user/admin/' + uuid + '/',
        method: 'delete'
    });
}
