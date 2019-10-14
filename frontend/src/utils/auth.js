import Cookies from 'js-cookie';

const TokenKey = 'vue_admin_template_token';

export function getToken() {
    return Cookies.get(TokenKey);
}

export function setToken(token) {
    return Cookies.set(TokenKey, token);
}

export function removeToken() {
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
