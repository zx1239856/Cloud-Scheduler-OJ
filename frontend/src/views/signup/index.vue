<template>
  <div class="signup-container">
    <el-form
      ref="signupForm"
      :model="signupForm"
      :rules="signupRules"
      auto-complete="off"
      class="signup-form"
      label-position="left"
    >
      <div class="title-container">
        <h3 class="title">Cloud Scheduler Sign Up</h3>
      </div>

      <el-form-item prop="email">
        <span class="svg-container">
          <svg-icon icon-class="email" />
        </span>
        <el-input
          ref="email"
          v-model="signupForm.email"
          auto-complete="off"
          name="email"
          placeholder="Email"
          tabindex="1"
          type="text"
        />
      </el-form-item>

      <el-form-item prop="username">
        <span class="svg-container">
          <svg-icon icon-class="user" />
        </span>
        <el-input
          ref="username"
          v-model="signupForm.username"
          auto-complete="off"
          name="username"
          placeholder="Username"
          tabindex="1"
          type="text"
        />
      </el-form-item>

      <el-form-item prop="password">
        <span class="svg-container">
          <svg-icon icon-class="password" />
        </span>
        <el-input
          :key="passwordType"
          ref="password"
          v-model="signupForm.password"
          :type="passwordType"
          auto-complete="off"
          name="password"
          placeholder="Password"
          tabindex="2"
        />
        <span class="show-pwd" @click="showPwd">
          <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
        </span>
      </el-form-item>

      <el-form-item prop="confirmPassword">
        <span class="svg-container">
          <svg-icon icon-class="password" />
        </span>
        <el-input
          :key="confirmPasswordType"
          ref="confirmPassword"
          v-model="signupForm.confirmPassword"
          :type="confirmPasswordType"
          auto-complete="off"
          name="confirmPassword"
          placeholder="Confirm Password"
          tabindex="3"
          @keyup.enter.native="handleSignup"
        />
        <span class="show-pwd" @click="showConfirmPwd">
          <svg-icon :icon-class="confirmPasswordType === 'password' ? 'eye' : 'eye-open'" />
        </span>
      </el-form-item>

      <el-button
        :loading="loading"
        style="width:100%;margin-bottom:30px;"
        type="primary"
        @click.native.prevent="handleSignup"
      >Sign Up</el-button>
      <router-link to="/login/" class="link">Aready a member? Log in!</router-link>
    </el-form>
  </div>
</template>

<script>
import { validateEmail } from '@/utils/validate';

export default {
    name: 'SignUp',
    data() {
        const validateUsername = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('Username cannot be empty'));
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
        const validateConfirmPassword = (rule, value, callback) => {
            if (value.length === 0) {
                callback(new Error('Password cannot be empty'));
            } else if (value !== this.$refs.password.value) {
                callback(new Error('Please confirm your password'));
            } else {
                callback();
            }
        };
        const emailValidator = (rule, value, callback) => {
            if (!validateEmail(value)) {
                callback(new Error('Please enter a valid email address'));
            } else {
                callback();
            }
        };
        return {
            signupForm: {
                email: '',
                username: '',
                password: '',
                confirmPassword: ''
            },
            signupRules: {
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
                ],
                confirmPassword: [
                    {
                        required: true,
                        trigger: 'blur',
                        validator: validateConfirmPassword
                    }
                ],
                email: [
                    {
                        required: true,
                        trigger: 'blur',
                        validator: emailValidator
                    }
                ]
            },
            loading: false,
            passwordType: 'password',
            confirmPasswordType: 'password',
            redirect: undefined
        };
    },
    watch: {
        $route: {
            handler: function(route) {
                this.redirect = route.query && route.query.redirect;
            },
            immediate: true
        }
    },
    mounted() {
        this.$nextTick(() => {
            this.$refs.email.focus();
        });
    },
    methods: {
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
        showConfirmPwd() {
            if (this.confirmPasswordType === 'password') {
                this.confirmPasswordType = '';
            } else {
                this.confirmPasswordType = 'password';
            }
            this.$nextTick(() => {
                this.$refs.confirmPassword.focus();
            });
        },
        handleSignup() {
            this.$refs.signupForm.validate(valid => {
                if (valid) {
                    this.loading = true;
                    this.$store
                        .dispatch('user/signup', this.signupForm)
                        .then(() => {
                            this.$message({
                                message: 'Sign Up Success',
                                type: 'success'
                            });
                            this.loading = false;
                            this.$router.push('/login');
                        })
                        .catch(() => {
                            this.loading = false;
                        });
                } else {
                    return false;
                }
            });
        }
    }
};
</script>

<style lang="scss">
/* 修复input 背景不协调 和光标变色 */
/* Detail see https://github.com/PanJiaChen/vue-element-admin/pull/927 */

$bg: #283443;
$light_gray: #fff;
$cursor: #fff;

@supports (-webkit-mask: none) and (not (cater-color: $cursor)) {
    .signup-container .el-input input {
        color: $cursor;
    }
}

/* reset element-ui css */
.signup-container {
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

.signup-container {
    min-height: 100%;
    width: 100%;
    background-color: $bg;
    overflow: hidden;

    .signup-form {
        position: relative;
        width: 520px;
        max-width: 100%;
        padding: 120px 35px 0;
        margin: 0 auto;
        overflow: hidden;
    }

    .tips {
        font-size: 14px;
        color: #fff;
        margin-bottom: 10px;

        span {
            &:first-of-type {
                margin-right: 16px;
            }
        }
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

    .link {
        color: #fff;
        float: right;
        text-decoration: underline;
    }
}
</style>
