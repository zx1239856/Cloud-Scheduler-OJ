<template>
  <div class="app-container">
    <el-form ref="dialogForm" :rules="dialogRules" :model="formData" label-position="left" label-width="200px" style="margin:50px; width:600px;">

      <el-form-item label="Name" prop="name">
        <el-input v-model="formData.name" placeholder="Task Settings Name" />
      </el-form-item>

      <el-form-item label="Description" prop="description">
        <el-input v-model="formData.description" placeholder="This is a demo" />
      </el-form-item>

      <el-form-item label="Image" prop="image">
        <el-input v-model="formData.image" placeholder="nginx:latest" />
      </el-form-item>
      <el-form-item label="Persistent Volume">
        <el-select v-model="formData.persistent_volume_name" placeholder="cephfs-pvc">
          <el-option label="cephfs-pvc" value="cephfs-pvc" />
        </el-select>
      </el-form-item>
      <el-form-item label="Mount Path" prop="persistent_volume_mount_path">
        <el-input v-model="formData.persistent_volume_mount_path" placeholder="/var/image/" />
      </el-form-item>
      <el-form-item label="Shell" prop="shell">
        <el-input v-model="formData.shell" placeholder="/bin/bash" />
      </el-form-item>
      <el-form-item label="Commands" prop="commands">
        <el-input v-model="formData.commands" type="textarea" :autosize="{ minRows: 4, maxRows: 4}" placeholder="echo hello world" />
      </el-form-item>

      <el-form-item label="Memory Limit" prop="memory_limit">
        <el-input v-model="formData.memory_limit" placeholder="128M" />
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
        <el-input-number v-model="formData.time_limit" />
      </el-form-item>
      <el-form-item label="Replica" prop="replica">
        <el-input-number v-model="formData.replica" />
      </el-form-item>
      <el-form-item label="TTL Interval" prop="ttl_interval">
        <el-input-number v-model="formData.ttl_interval" />
      </el-form-item>
      <el-form-item label="Max Sharing Users" prop="max_sharing_users">
        <el-input-number v-model="formData.max_sharing_users" />
      </el-form-item>

      <div align="center">
        <el-button @click="handleCancel()">
          Cancel
        </el-button>
        <el-button type="primary" @click="handleConfirm()">
          {{ confirmMessage }}
        </el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { getTaskSettings, createTaskSettings, updateTaskSettings } from '@/api/task_settings';

export default {
    data() {
        return {
            confirmMessage: 'Create',
            formData: {
                name: '',
                description: '',
                image: '',
                persistent_volume_name: '',
                persistent_volume_mount_path: '',
                shell: '',
                commands: '',
                memory_limit: '',
                time_limit: 900,
                replica: 2,
                ttl_interval: 5,
                max_sharing_users: 1
            },
            dialogRules: {
                name: [{
                    required: true,
                    message: 'Name is required',
                    trigger: 'blur'
                }],
                image: [{
                    required: true,
                    message: 'Image is required',
                    trigger: 'blur'
                }],
                shell: [{
                    required: true,
                    message: 'Shell is required',
                    trigger: 'blur'
                }],
                persistent_volume_name: [{
                    required: true,
                    message: 'Persistent volume is required',
                    trigger: 'blur'
                }],
                persistent_volume_mount_path: [{
                    required: true,
                    message: 'Mount path is required',
                    trigger: 'blur'
                }],
                memory_limit: [{
                    required: true,
                    message: 'Memory Limit is required',
                    trigger: 'blur'
                }],
                working_path: [{
                    required: true,
                    message: 'Working path is required',
                    trigger: 'blur'
                }],
                task_script_path: [{
                    required: true,
                    message: 'Task script path is required',
                    trigger: 'blur'
                }],
                task_initial_file_path: [{
                    required: true,
                    message: 'Task initial file path is required',
                    trigger: 'blur'
                }]
            }
        };
    },
    created() {
        if (this.$route.query.settings_uuid) {
            // update
            this.confirmMessage = 'Update';
            getTaskSettings(this.$route.query.settings_uuid).then(response => {
                this.formData = this.toFrontendForm(response.payload);
            });
        }
    },
    methods: {
        toBackendForm(form) {
            return {
                name: form.name,
                description: form.description,
                container_config: {
                    image: form.image,
                    persistent_volume: {
                        name: form.persistent_volume_name,
                        mount_path: form.persistent_volume_mount_path
                    },
                    shell: form.shell,
                    commands: form.commands.split('\n'),
                    memory_limit: form.memory_limit,
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
                image: form.container_config.image,
                persistent_volume_name: form.container_config.persistent_volume.name,
                persistent_volume_mount_path: form.container_config.persistent_volume.mount_path,
                shell: form.container_config.shell,
                commands: form.container_config.commands.join('\n'),
                memory_limit: form.container_config.memory_limit,
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
                if (valid) {
                    const backendForm = this.toBackendForm(this.formData);
                    if (this.$route.query.settings_uuid) {
                        updateTaskSettings(this.$route.query.settings_uuid, backendForm).then(response => {
                            this.$message({
                                message: 'Update Success',
                                type: 'success'
                            });
                            this.$router.back();
                        });
                    } else {
                        createTaskSettings(backendForm).then(response => {
                            this.$message({
                                message: 'Create Success',
                                type: 'success'
                            });
                            this.$router.back();
                        });
                    }
                } else {
                    return false;
                }
            });
        }
    }
};
</script>
