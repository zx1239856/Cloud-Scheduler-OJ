<template>
  <div class="dashboard-container">
    <el-button class="filter-item" style="margin: 10px;" type="primary" icon="el-icon-plus" @click="handleCreate">
      Upload File
    </el-button>
    <div class="dashboard-text">Hello, {{ name }} !</div>
    <!--
    <el-dialog :title="dialogType" :visible.sync="dialogFormVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="dialogData" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;">
        <el-form-item label="Name" prop="name">
          <el-input v-model="dialogData.name" />
        </el-form-item>
        <el-form-item label="Concurrency" prop="concurrency">
          <el-slider v-model="dialogData.concurrency" show-input />
        </el-form-item>
        <el-form-item label="Config" prop="task_config">
          <el-input v-model="dialogData.task_config" :autosize="{ minRows: 4, maxRows: 10}" type="textarea" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Cancel
        </el-button>
        <el-button type="primary" @click="handleDialogConfirm">
          Confirm
        </el-button>
      </div>
    </el-dialog>
    -->
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'Dashboard',
    computed: {
        ...mapGetters(['name'])
    },
    methods: {
        handleCreate() {
            this.dialogFormVisible = true;
            this.dialogType = 'Create';
        }
    }
};
</script>

<style lang="scss" scoped>
.dashboard {
    &-container {
        margin: 30px;
    }
    &-text {
        font-size: 30px;
        line-height: 46px;
        text-align: center;
        margin-top: 40vh;
    }
}
</style>
