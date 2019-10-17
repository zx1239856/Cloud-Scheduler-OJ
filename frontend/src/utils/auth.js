import Cookies from 'js-cookie';

const TokenKey = 'admin_token';

export function getToken() {
    return Cookies.get(TokenKey);
}

export function setToken(token) {
    return Cookies.set(TokenKey, token);
}

export function removeToken() {
    return Cookies.remove(TokenKey);
}

const AvatarKey = 'avatar_url';

export function setAvatar(avatar) {
    return Cookies.set(AvatarKey, avatar);
}

export function getAvatar() {
    return Cookies.get(AvatarKey);
}

export function removeAvatar() {
    return Cookies.remove(TokenKey);
}

const UsernameKey = 'UsernameKey';

export function getUsername() {
    return Cookies.get(UsernameKey);
}

export function setUsername(username) {
    return Cookies.set(UsernameKey, username);
}

export function removeUsername() {
    return Cookies.remove(UsernameKey);
}
