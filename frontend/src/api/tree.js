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

export function updateFile(settingsUuid, filename, content) {
    return request({
        url: '/user_space/' + settingsUuid + '/',
        method: 'put',
        data: {
            file: filename,
            old_file: filename,
            content: content
        }
    });
}

export function renameFile(settingsUuid, oldFilename, newFilename) {
    return request({
        url: '/user_space/' + settingsUuid + '/',
        method: 'put',
        data: {
            old_file: oldFilename,
            file: newFilename
        }
    });
}

export function renameDirectory(settingsUuid, oldDir, newDir) {
    return request({
        url: '/user_space/' + settingsUuid + '/',
        method: 'put',
        data: {
            old_path: oldDir,
            path: newDir
        }
    });
}

export function createFile(settingsUuid, filename) {
    return request({
        url: '/user_space/' + settingsUuid + '/',
        method: 'post',
        data: {
            file: filename
        }
    });
}

export function createDirectory(settingsUuid, dirName) {
    return request({
        url: '/user_space/' + settingsUuid + '/',
        method: 'post',
        data: {
            path: dirName
        }
    });
}

export function deleteFile(settingsUuid, filename) {
    return request({
        url: '/user_space/' + settingsUuid + '/',
        method: 'delete',
        data: {
            file: filename
        }
    });
}

export function deleteDirectory(settingsUuid, dirName) {
    return request({
        url: '/user_space/' + settingsUuid + '/',
        method: 'delete',
        data: {
            path: dirName
        }
    });
}
