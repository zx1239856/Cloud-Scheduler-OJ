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
        <el-input v-model="formData.container_config.image" placeholder="nginx:latest" />
      </el-form-item>
      <el-form-item label="Persistent Volumn" prop="persistent_volume_name">
        <el-input v-model="formData.container_config.persistent_volume.name" placeholder="ceph-pvc" />
      </el-form-item>
      <el-form-item label="Mount Path" prop="persistent_volume_mount_path">
        <el-input v-model="formData.container_config.persistent_volume.mount_path" placeholder="/var/image/" />
      </el-form-item>
      <el-form-item label="Shell" prop="shell">
        <el-input v-model="formData.container_config.shell" placeholder="/bin/bash" />
      </el-form-item>
      <el-form-item label="Commands" prop="commands">
        <el-input v-model="formData.container_config.commands_display" type="textarea" :autosize="{ minRows: 4, maxRows: 4}" placeholder="echo hello world" />
      </el-form-item>

      <el-form-item label="Memory Limit" prop="memory_limit">
        <el-input v-model="formData.container_config.memory_limit" placeholder="128M" />
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
                container_config: {
                    image: '',
                    persistent_volume: {
                        name: '',
                        mount_path: ''
                    },
                    shell: '',
                    commands: undefined,
                    commands_display: '',
                    memory_limit: ''
                },
                time_limit: 900,
                replica: 2,
                ttl_interval: 5,
                max_sharing_users: 1
            },
            dialogRules: {
                name: [{
                    required: true,
                    message: 'name is required',
                    trigger: 'blur'
                }]
                // persistent_volume_name: [{
                //     required: true,
                //     message: 'Name is required',
                //     trigger: 'blur'
                // }],
                // persistent_volume_mount_path: [{
                //     required: true
                //     // message: 'Mount Path is required'
                //     // trigger: 'blur'
                // }],
                // memory_limit: [{
                //     required: true,
                //     message: 'Memory Limit is required'
                // }]
            }
        };
    },
    created() {
        if (this.$route.query.settings_uuid) {
            // if update
            this.confirmMessage = 'Update';
            getTaskSettings(this.$route.query.settings_uuid).then(response => {
                this.formData = response.payload;
                this.formData.container_config.commands_display = this.formData.container_config.commands.join('\n');
            });
        }
    },
    methods: {
        handleCancel() {
            this.$router.back();
        },
        handleConfirm() {
            this.formData.container_config.commands = this.formData.container_config.commands_display.split('\n');
            if (this.$route.query.settings_uuid) {
                updateTaskSettings(this.$route.query.settings_uuid, this.formData).then(response => {
                    this.$message({
                        message: 'Update Success',
                        type: 'success'
                    });
                    this.$router.back();
                });
            } else {
                createTaskSettings(this.formData).then(response => {
                    this.$message({
                        message: 'Create Success',
                        type: 'success'
                    });
                    this.$router.back();
                });
            }
        }
    }
};
</script>
