<template>
  <div class="profile-container">
    <el-card style="margin-bottom: 20px;">

      <div slot="header" class="clearfix">
        <span>About Me</span>
      </div>

      <div class="user-profile">
        <div class="box-center">
          <el-avatar class="avatar" :size="100" :src="avatar" />
        </div>
        <div class="box-center">
          <div class="user-name text-center">{{ profile.username }}</div>
          <div class="user-role text-center text-muted">{{ profile.email }}</div>
        </div>
      </div>

      <el-button type="primary" icon="el-icon-edit" class="edit-button" plain @click="handleEditProfile">Edit Profile</el-button>

    </el-card>

    <el-dialog title="Update User Info" :visible.sync="dialogVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="profile" enctype="multipart/form-data" label-position="left" label-width="200px" style="width: 500px; margin-left:50px;">
        <el-form-item label="Email" prop="email">
          <el-input v-model="profile.email" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input ref="password" v-model="profile.password" type="password" />
        </el-form-item>
        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input v-model="profile.confirmPassword" type="password" @keyup.enter.native="handleDialogConfirm" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">
          Cancel
        </el-button>
        <el-button type="primary" @click="handleDialogConfirm">
          Update
        </el-button>
      </div>

    </el-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { getInfo, updateUserInfo } from '@/api/user';
const md5 = require('js-md5');

export default {
    name: 'Profile',

    data() {
        const validateConfirmPassword = (rule, value, callback) => {
            if (value !== this.$refs.password.value) {
                callback(new Error('Please re-confirm your password'));
            } else {
                callback();
            }
        };
        return {
            profile: {
                username: '',
                email: '',
                password: '',
                confirmPassword: ''
            },
            dialogVisible: false,
            dialogRules: {
                email: [{
                    required: true,
                    message: 'Please enter your new email',
                    trigger: 'blur'
                }],
                password: [{
                    required: true,
                    message: 'Please enter your new password',
                    trigger: 'blur'
                }],
                confirmPassword: [{
                    required: true,
                    message: 'Please confirm your password',
                    validator: validateConfirmPassword,
                    trigger: 'blur'
                }]
            }
        };
    },
    computed: {
        ...mapGetters([
            'avatar'
        ])
    },
    created() {
        getInfo().then(response => {
            this.profile.username = response.payload.username;
            this.profile.email = response.payload.email;
        });
    },
    methods: {
        handleEditProfile() {
            this.dialogVisible = true;
            this.profile.password = '';
            this.profile.confirmPassword = '';
        },
        handleDialogConfirm() {
            this.$refs.dialogForm.validate(valid => {
                if (!valid) {
                    return false;
                }

                updateUserInfo(this.profile.email, md5(this.profile.password))
                    .then(response => {
                        this.$message({
                            message: 'Successfully Updated',
                            type: 'success'
                        });
                        this.dialogVisible = false;
                    });
            });
        }
    }
};
</script>

<style lang='scss'>
.clearfix:before,
.clearfix:after {
    display: table;
    content: "";
}

.clearfix:after {
    clear: both
}

.text-muted {
    color: #777;
}

.profile-container{
    width: 360px;
    text-align: center;
    margin: auto;
    position: absolute;
    margin-top: 14vh;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    .edit-button{
        margin: 20px;
    }
}

.user-profile {
    .user-name {
        font-weight: bold;
        font-size: 32px;
    }

    .box-center {
        padding: 10px;
    }

    .user-role {
        padding-top: 10px;
        font-weight: 400;
        font-size: 14px;
    }

    .box-social {
        padding-top: 30px;

        .el-table {
        border-top: 1px solid #dfe6ec;
        }
    }

    .user-follow {
        padding-top: 20px;
    }
}

.user-bio {
    margin-top: 20px;
    color: #606266;

    span {
        padding-left: 4px;
    }

    .user-bio-section {
        font-size: 14px;
        padding: 15px 0;

        .user-bio-section-header {
        border-bottom: 1px solid #dfe6ec;
        padding-bottom: 10px;
        margin-bottom: 10px;
        font-weight: bold;
        }
    }
}
</style>
