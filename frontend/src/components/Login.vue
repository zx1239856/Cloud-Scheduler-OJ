<template>
    <div class="login-container">
        <el-form
            :model="loginForm"
            :rules="loginRules"
            autocomplete="off"
            class="login-form"
            label-position="left"
            ref="loginForm"
        >
            <div class="title-container">
                <h3 class="title">云资源管理平台</h3>
            </div>

            <el-form-item prop="username">
                <span class="svg-container">
                    <svg-icon icon-class="user" />
                </span>
                <el-input
                    autocomplete="off"
                    name="username"
                    placeholder="Username"
                    ref="username"
                    tabindex="1"
                    type="text"
                    v-model="loginForm.username"
                />
            </el-form-item>

            <el-tooltip content="Caps lock is On" manual placement="right" v-model="capsTooltip">
                <el-form-item prop="password">
                    <span class="svg-container">
                        <svg-icon icon-class="password" />
                    </span>
                    <el-input
                        :key="passwordType"
                        :type="passwordType"
                        @blur="capsTooltip = false"
                        @keyup.enter.native="handleLogin"
                        @keyup.native="checkCapslock"
                        autocomplete="off"
                        name="password"
                        placeholder="Password"
                        ref="password"
                        tabindex="2"
                        v-model="loginForm.password"
                    />
                    <span @click="showPwd" class="show-pwd">
                        <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
                    </span>
                </el-form-item>
            </el-tooltip>

            <el-button
                :loading="loading"
                @click.native.prevent="handleLogin"
                style="width:100%;margin-bottom:30px;"
                type="primary"
            >Login</el-button>
        </el-form>

        <!-- <el-dialog :visible.sync="showDialog" title="Or connect with">
            Can not be simulated on local, so please combine you own business simulation! ! !
            <br />
            <br />
            <br />
            <social-sign />
        </el-dialog>-->
    </div>
</template>

<script>
export default {
    name: 'Login',
    data() {
        const validateUsername = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('User name cannot be empty'));
            } else {
                callback();
            }
        };
        const validatePassword = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('Password cannot be empty'));
            } else {
                callback();
            }
        };
        return {
            loginForm: {
                username: '',
                password: ''
            },
            loginRules: {
                username: [
                    {
                        required: true,
                        trigger: 'blur',
                        validator: validateUsername
                    }
                ],
                password: [
                    {
                        required: true,
                        trigger: 'blur',
                        validator: validatePassword
                    }
                ]
            },
            passwordType: 'password',
            capsTooltip: false,
            loading: false,
            showDialog: false,
            redirect: undefined,
            otherQuery: {}
        };
    },
    watch: {
        $route: {
            handler: function(route) {
                const query = route.query;
                if (query) {
                    this.redirect = query.redirect;
                    // this.otherQuery = this.getOtherQuery(query);
                }
            },
            immediate: true
        }
    },
    created() {
        // window.addEventListener('storage', this.afterQRScan)
    },
    mounted() {
        if (this.loginForm.username === '') {
            this.$refs.username.focus();
        } else if (this.loginForm.password === '') {
            this.$refs.password.focus();
        }
    },
    methods: {
        handleLogin: function() {
            this.$refs.loginForm.validate(valid => {
                if (valid) {
                    this.loading = true;
                    this.$router.push('/web-ssh');
                } else {
                    console.log('submit error');
                    return false;
                }
            });
        },
        showPwd() {
            if (this.passwordType === 'password') {
                this.passwordType = '';
            } else {
                this.passwordType = 'password';
            }
            this.$nextTick(() => {
                this.$refs.password.focus();
            });
        },
        checkCapslock({ shiftKey, key } = {}) {
            if (key && key.length === 1) {
                if (
                    (shiftKey && (key >= 'a' && key <= 'z')) ||
                    (!shiftKey && (key >= 'A' && key <= 'Z'))
                ) {
                    this.capsTooltip = true;
                } else {
                    this.capsTooltip = false;
                }
            }
            if (key === 'CapsLock' && this.capsTooltip === true) {
                this.capsTooltip = false;
            }
        }
    }
};
</script>

<style lang="scss">
/* fix input background and cursor color */
/* Detail see https://github.com/PanJiaChen/vue-element-admin/pull/927 */

$bg: #283443;
$light_gray: #fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
    .login-container .el-input input {
        color: $cursor;
    }
}

/* reset element-ui css */
.login-container {
    min-height: 100%;
    width: 100%;
    height: 100%;
    .el-input {
        display: inline-block;
        height: 47px;
        width: 85%;

        input {
            background: transparent;
            border: 0px;
            -webkit-appearance: none;
            border-radius: 0px;
            padding: 12px 5px 12px 15px;
            color: $light_gray;
            height: 47px;
            caret-color: $cursor;

            &:-webkit-autofill {
                box-shadow: 0 0 0px 1000px $bg inset !important;
                -webkit-text-fill-color: $cursor !important;
            }
        }
    }

    .el-form-item {
        border: 1px solid rgba(255, 255, 255, 0.1);
        background: rgba(0, 0, 0, 0.1);
        border-radius: 5px;
        color: #454545;
    }
}
</style>

<style lang="scss" scoped>
$bg: #2d3a4b;
$dark_gray: #889aa4;
$light_gray: #eee;
body {
    margin: 0;
}
.login-container {
    // min-height: 100%;
    height: 100vh;
    width: 100vw;
    margin-top: 0px;

    background-color: $bg;
    overflow: hidden;

    .login-form {
        position: relative;
        width: 520px;
        max-width: 100%;
        padding: 160px 35px 0;
        margin: 0 auto;
        overflow: hidden;
    }

    .svg-container {
        padding: 6px 5px 6px 15px;
        color: $dark_gray;
        vertical-align: middle;
        width: 30px;
        display: inline-block;
    }

    .title-container {
        position: relative;

        .title {
            font-size: 26px;
            color: $light_gray;
            margin: 0px auto 40px auto;
            text-align: center;
            font-weight: bold;
        }
    }

    .show-pwd {
        position: absolute;
        right: 10px;
        top: 7px;
        font-size: 16px;
        color: $dark_gray;
        cursor: pointer;
        user-select: none;
    }
}
</style>
