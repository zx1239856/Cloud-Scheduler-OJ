import { login, logout, getInfo, signup } from '@/api/user';
// import { resetRouter } from '@/router';

const md5 = require('js-md5');

const state = {
    token: '',
    name: '',
    avatar: '',
    permission: ''
};

const mutations = {
    SET_TOKEN: (state, token) => {
        state.token = token;
    },
    SET_NAME: (state, name) => {
        state.name = name;
    },
    SET_AVATAR: (state, avatar) => {
        state.avatar = avatar;
    },
    SET_PERMISSION: (state, permission) => {
        state.permission = permission;
    }
};

const actions = {
    // user login
    login({ commit }, userInfo) {
        const { username, password } = userInfo;

        return new Promise((resolve, reject) => {
            return login({ username: username.trim(), password: md5(password) }).then(response => {
                const { payload } = response;
                commit('SET_TOKEN', payload.token);
                commit('SET_NAME', payload.username);
                commit('SET_AVATAR', payload.avatar);
                commit('SET_PERMISSION', payload.permission);
                resolve();
            }).catch(error => {
                reject(error);
            });
        });
    },

    // user signup
    signup({ commit }, userInfo) {
        const { username, password, email } = userInfo;
        return new Promise((resolve, reject) => {
            return signup({ username: username.trim(), password: md5(password), email: email }).then(response => {
                // const { data } = response;
                // commit('SET_TOKEN', data.token);
                // setToken(data.token);
                resolve();
            }).catch(error => {
                reject(error);
            });
        });
    },

    // get user info
    getInfo({ commit, state }) {
        return new Promise((resolve, reject) => {
            getInfo(state.token).then(response => {
                console.log(response);
                const { payload } = response;

                if (!payload) {
                    reject('Verification failed, please Login again.');
                }

                const { username, avatar } = payload;

                commit('SET_NAME', username);
                commit('SET_AVATAR', avatar);
                resolve(payload);
            }).catch(error => {
                reject(error);
            });
        });
    },

    // user logout
    async logout({ commit, state }) {
        return new Promise((resolve, reject) => {
            logout(state.token).then(() => {
                commit('SET_TOKEN', '');
                commit('SET_AVATAR', '');
                commit('SET_NAME', '');
                commit('SET_PERMISSION', '');
                // resetRouter();
                resolve();
            }).catch(error => {
                reject(error);
            });
        });
    },

    // remove token
    resetToken({ commit }) {
        return new Promise(resolve => {
            commit('SET_TOKEN', '');
            commit('SET_AVATAR', '');
            commit('SET_NAME', '');
            commit('SET_PERMISSION', '');
            resolve();
        });
    }
};

export default {
    namespaced: true,
    state,
    mutations,
    actions
};

