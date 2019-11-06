import request from '@/utils/request';
import filerequest from '@/utils/file-request';

export function getFileList(query) {
    return request({
        url: '/storage/upload_file/',
        method: 'get',
        params: query
    });
}

export function uploadFile(query) {
    return filerequest({
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

// File Web IDE

export function createPod(pvcname) {
    return request({
        url: '/storage/pod/',
        method: 'post',
        data: { pvcname: pvcname }
    });
}

export function deletePod(pvcname) {
    return request({
        url: '/storage/pod/',
        method: 'delete',
        data: { pvcname: pvcname }
    });
}

export function getTreePath(pvcname, path) {
    return request({
        url: '/storage/ide/' + pvcname + '/',
        method: 'get',
        params: { path: path }
    });
}

export function getFile(pvcname, file) {
    return request({
        url: '/storage/ide/' + pvcname + '/',
        method: 'get',
        params: { file: file }
    });
}

export function updateFile(pvcname, filename, content) {
    return request({
        url: '/storage/ide/' + pvcname + '/',
        method: 'put',
        data: {
            file: filename,
            old_file: filename,
            content: content
        }
    });
}

export function renameFile(pvcname, oldFilename, newFilename) {
    return request({
        url: '/storage/ide/' + pvcname + '/',
        method: 'put',
        data: {
            old_file: oldFilename,
            file: newFilename
        }
    });
}

export function renameDirectory(pvcname, oldDir, newDir) {
    return request({
        url: '/storage/ide/' + pvcname + '/',
        method: 'put',
        data: {
            old_path: oldDir,
            path: newDir
        }
    });
}

export function createFile(pvcname, filename) {
    return request({
        url: '/storage/ide/' + pvcname + '/',
        method: 'post',
        data: {
            file: filename
        }
    });
}

export function createDirectory(pvcname, dirName) {
    return request({
        url: '/storage/ide/' + pvcname + '/',
        method: 'post',
        data: {
            path: dirName
        }
    });
}

export function deleteFile(pvcname, filename) {
    return request({
        url: '/storage/ide/' + pvcname + '/',
        method: 'delete',
        data: {
            file: filename
        }
    });
}

export function deleteDirectory(pvcname, dirName) {
    return request({
        url: '/storage/ide/' + pvcname + '/',
        method: 'delete',
        data: {
            path: dirName
        }
    });
}
