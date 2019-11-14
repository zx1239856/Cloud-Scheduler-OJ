<template>
  <div class="app-container">
    <el-form ref="dialogForm" :rules="dialogRules" :model="formData" label-position="left" label-width="200px" style="margin:50px; width: 700px;">

      <el-form-item label="Name" prop="name">
        <el-input ref="inputName" v-model="formData.name" placeholder="Task Settings Name" />
      </el-form-item>

      <el-form-item label="Description" prop="description">
        <el-input v-model="formData.description" placeholder="This is a demo" />
      </el-form-item>

      <el-form-item label="Image" prop="image">
        <el-col :span="18">
          <el-select
            v-model="formData.image"
            filterable
            allow-create
            default-first-option
            placeholder="Image"
            style="width: 100%;"
            @change="handleImageChange"
          >
            <el-option v-for="repo in repoList" :key="'registry.dropthu.online:30443/' + repo.Repo" :label="'registry.dropthu.online:30443/' + repo.Repo" :value="repoPrefix + repo.Repo" />
          </el-select>
        </el-col>
        <el-col class="line" :span="1" style="text-align: center;">:</el-col>
        <el-col :span="5">
          <el-select
            v-model="formData.tag"
            :loading="tagLoading"
            filterable
            allow-create
            default-first-option
            placeholder="Tag"
            style="width: 100%;"
          >
            <el-option v-for="tag in tagList" :key="tag.Tag" :label="tag.Tag" :value="tag.Tag" />
          </el-select>
        </el-col>
      </el-form-item>
      <el-form-item label="Persistent Volume">
        <el-select v-model="formData.persistent_volume_name" placeholder="Select Persistent Volume" style="width: 100%;">
          <el-option
            v-for="item in pvcList"
            :key="item.name"
            :label="item.name"
            :value="item.name"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="Mount Path" prop="persistent_volume_mount_path">
        <el-input v-model="formData.persistent_volume_mount_path" placeholder="/var/image/" />
      </el-form-item>
      <el-form-item label="Shell" prop="shell">
        <el-input v-model="formData.shell" placeholder="/bin/bash" />
      </el-form-item>
      <el-form-item label="Commands" prop="commands">
        <el-input v-model="formData.commands" type="textarea" :autosize="{ minRows: 5, maxRows: 100}" placeholder="echo hello world" />
      </el-form-item>

      <el-form-item label="Memory Limit" prop="memory_limit">
        <el-input v-model="formData.memory_limit" placeholder="128">
          <el-radio-group slot="append" v-model="formData.memory_limit_unit">
            <el-radio-button label="K" />
            <el-radio-button label="M" />
            <el-radio-button label="G" />
          </el-radio-group>
        </el-input>
      </el-form-item>
      <el-form-item label="Working Path" prop="working_path">
        <el-input v-model="formData.working_path" placeholder="/home/task/" />
      </el-form-item>
      <el-form-item label="Task Script Path" prop="task_script_path">
        <el-input v-model="formData.task_script_path" placeholder="scripts/" />
      </el-form-item>
      <el-form-item label="Task Initial File Path" prop="task_initial_file_path">
        <el-input v-model="formData.task_initial_file_path" placeholder="initial/" />
      </el-form-item>

      <el-form-item label="Time Limit" prop="time_limit">
        <el-input-number v-model="formData.time_limit" :min="1" />
      </el-form-item>
      <el-form-item label="Replica" prop="replica">
        <el-input-number v-model="formData.replica" :min="1" />
      </el-form-item>
      <el-form-item label="TTL Interval" prop="ttl_interval">
        <el-input-number v-model="formData.ttl_interval" :min="1" />
      </el-form-item>
      <el-form-item label="Max Sharing Users" prop="max_sharing_users">
        <el-input-number v-model="formData.max_sharing_users" :min="1" />
      </el-form-item>

      <div align="center">
        <el-button @click="handleCancel()">
          Cancel
        </el-button>
        <el-button :loading="dialogLoading" type="primary" @click="handleConfirm()">
          {{ confirmMessage }}
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { getTaskSettings, createTaskSettings, updateTaskSettings } from '@/api/task_settings';
import { validatePath } from '@/utils/validate';
import { getRepositories, getRepository } from '@/api/registry';
import { getPVCList } from '@/api/storage';

export default {
    data() {
        const errorMessage = 'Invalid input';
        const pathValidator = (rule, value, callback) => {
            if (validatePath(value)) {
                callback();
            } else {
                callback(new Error(errorMessage));
            }
        };
        return {
            tagLoading: false,
            repoPrefix: 'registry.dropthu.online:30443/',
            repoList: [],
            tagList: [],
            select: 'G',
            confirmMessage: 'Create',
            dialogLoading: false,
            formData: {
                name: '',
                description: '',
                image: '',
                tag: '',
                persistent_volume_name: '',
                persistent_volume_mount_path: '',
                shell: '',
                commands: '',
                memory_limit: '',
                memory_limit_unit: 'M',
                time_limit: 10,
                replica: 2,
                ttl_interval: 3,
                max_sharing_users: 1
            },
            pvcList: null,
            pvcCount: 0,
            dialogRules: {
                name: [{
                    required: true,
                    message: errorMessage,
                    trigger: 'blur'
                }],
                image: [{
                    required: true,
                    message: errorMessage,
                    trigger: 'blur'
                }],
                shell: [{
                    required: true,
                    message: errorMessage,
                    trigger: 'blur',
                    validator: pathValidator
                }],
                persistent_volume_name: [{
                    required: true,
                    message: errorMessage,
                    trigger: 'blur'
                }],
                persistent_volume_mount_path: [{
                    required: true,
                    message: errorMessage,
                    trigger: 'blur',
                    validator: pathValidator
                }],
                memory_limit: [{
                    required: true,
                    message: errorMessage,
                    trigger: 'blur',
                    validator: (rule, value, callback) => {
                        if (/^\d+$/.test(value) && !isNaN(Number(value))) {
                            callback();
                        } else {
                            callback(new Error(errorMessage));
                        }
                    }
                }],
                working_path: [{
                    required: true,
                    message: errorMessage,
                    trigger: 'blur',
                    validator: pathValidator
                }],
                task_script_path: [{
                    required: true,
                    message: errorMessage,
                    trigger: 'blur',
                    validator: pathValidator
                }],
                task_initial_file_path: [{
                    required: true,
                    message: errorMessage,
                    trigger: 'blur',
                    validator: pathValidator
                }]
            }
        };
    },
    mounted() {
        this.$nextTick(() => {
            this.$refs.inputName.focus();
        });
    },
    created() {
        if (this.$route.query.settings_uuid) {
            // update
            this.confirmMessage = 'Update';
            getTaskSettings(this.$route.query.settings_uuid).then(response => {
                this.formData = this.toFrontendForm(response.payload);
            });
        }
        this.getList();
        getRepositories().then(response => {
            this.repoList = response.payload.entity;
        });
    },
    methods: {
        handleImageChange(value) {
            this.tagList = [];
            this.formData.tag = '';
            if (value.startsWith(this.repoPrefix)) {
                this.tagLoading = true;
                const repoName = value.substr(this.repoPrefix.length);
                getRepository(repoName).then(response => {
                    this.tagList = response.payload.entity;
                }).finally(() => {
                    this.tagLoading = false;
                });
            }
        },
        getList() {
            getPVCList({ 'page': -1 }).then(response => {
                this.pvcList = response.payload.entry;
                this.pvcCount = response.payload.count;
            });
        },
        toBackendForm(form) {
            return {
                name: form.name,
                description: form.description,
                container_config: {
                    image: form.image + ':' + form.tag,
                    persistent_volume: {
                        name: form.persistent_volume_name,
                        mount_path: form.persistent_volume_mount_path
                    },
                    shell: form.shell,
                    commands: form.commands.split('\n'),
                    memory_limit: form.memory_limit + form.memory_limit_unit,
                    working_path: form.working_path,
                    task_script_path: form.task_script_path,
                    task_initial_file_path: form.task_initial_file_path
                },
                time_limit: form.time_limit,
                replica: form.replica,
                ttl_interval: form.ttl_interval,
                max_sharing_users: form.max_sharing_users
            };
        },
        toFrontendForm(form) {
            return {
                name: form.name,
                description: form.description,
                image: form.container_config.image.substr(0, form.container_config.image.lastIndexOf(':')),
                tag: form.container_config.image.substr(form.container_config.image.lastIndexOf(':') + 1),
                persistent_volume_name: form.container_config.persistent_volume.name,
                persistent_volume_mount_path: form.container_config.persistent_volume.mount_path,
                shell: form.container_config.shell,
                commands: form.container_config.commands.join('\n'),
                memory_limit: parseInt(form.container_config.memory_limit),
                memory_limit_unit: form.container_config.memory_limit.charAt(form.container_config.memory_limit.length - 1),
                working_path: form.container_config.working_path,
                task_script_path: form.container_config.task_script_path,
                task_initial_file_path: form.container_config.task_initial_file_path,
                time_limit: form.time_limit,
                replica: form.replica,
                ttl_interval: form.ttl_interval,
                max_sharing_users: form.max_sharing_users
            };
        },
        handleCancel() {
            this.$router.back();
        },
        handleConfirm() {
            this.$refs.dialogForm.validate(valid => {
                if (!valid) {
                    return false;
                }
                this.dialogLoading = true;
                const backendForm = this.toBackendForm(this.formData);
                if (this.$route.query.settings_uuid) {
                    updateTaskSettings(this.$route.query.settings_uuid, backendForm).then(response => {
                        this.$message({
                            message: 'Update Success',
                            type: 'success'
                        });
                        this.$router.back();
                    }).finally(() => {
                        this.dialogLoading = false;
                    });
                } else {
                    createTaskSettings(backendForm).then(response => {
                        this.$message({
                            message: 'Create Success',
                            type: 'success'
                        });
                        this.$router.back();
                    }).finally(() => {
                        this.dialogLoading = false;
                    });
                }
            });
        }
    }
};
</script>

<style lang="scss">
.el-input-group__append {
    background-color: #fff;
    border: none;
    padding: 0px;
}
</style>
