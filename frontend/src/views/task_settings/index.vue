<template>
  <div class="app-container">
    <div class="filter-container" align="right">
      <!-- <el-input v-model="listQuery.title" placeholder="Title" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" /> -->
      <!-- <el-select v-model="listQuery.importance" placeholder="Imp" clearable style="width: 90px" class="filter-item">
        <el-option v-for="item in importanceOptions" :key="item" :label="item" :value="item" />
      </el-select>
      <el-select v-model="listQuery.type" placeholder="Type" clearable class="filter-item" style="width: 130px">
        <el-option v-for="item in calendarTypeOptions" :key="item.key" :label="item.display_name+'('+item.key+')'" :value="item.key" />
      </el-select>
      <el-select v-model="listQuery.sort" style="width: 140px" class="filter-item" @change="handleFilter">
        <el-option v-for="item in sortOptions" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        Search
      </el-button> -->
      <el-button class="filter-item" style="margin: 10px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        Add
      </el-button>
    </div>

    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      @sort-change="sortChange"
    >
      <el-table-column label="UUID" width="400" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.uuid }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Name" min-width="150" align="center">
        <template slot-scope="{row}">
          <span>{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Created Time" width="250" align="center">
        <template slot-scope="scope">
          <span>{{ new Date(scope.row.create_time).toLocaleString() }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Concurrency" class-name="status-col" width="150" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.concurrency }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" width="150" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="small" icon="el-icon-edit" @click="handleUpdate(row)">
            Edit
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getList" />

    <el-dialog :title="dialogType" :visible.sync="dialogFormVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="dialogData" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;">
        <el-form-item label="Name" prop="name">
          <el-input v-model="dialogData.name" />
        </el-form-item>
        <el-form-item label="Concurrency">
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
  </div>
</template>

<script>
import { createTask, getTaskList, updateTask } from '@/api/tasks';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'PodList',
    components: { Pagination },
    directives: { waves },

    data() {
        const validConfig = (rule, value, callback) => {
            try {
                JSON.parse(value);
                callback();
            } catch {
                callback(new Error('Invalid config'));
            }
        };
        return {
            dialogType: 'Create',
            dialogFormVisible: false,
            tableKey: 0,
            list: null,
            total: 0,
            listLoading: true,
            pageSizes: [25],
            listQuery: {
                page: 1,
                limit: 25
            },
            dialogData: {
                uuid: undefined,
                concurrency: 5,
                name: '',
                task_config: '{}'
            },
            dialogRules: {
                name: [{
                    required: true,
                    message: 'name is required',
                    trigger: 'change'
                }],
                task_config: [{
                    required: true,
                    message: 'invalid config',
                    trigger: 'change',
                    validator: validConfig
                }]
            }
        };
    },
    created() {
        this.getList();
    },
    methods: {
        getList() {
            this.listLoading = true;

            getTaskList(this.listQuery).then(response => {
                this.list = response.payload.entry;
                this.total = response.payload.count;
                this.listLoading = false;
            });
        },
        handleCreate() {
            this.dialogFormVisible = true;
            this.dialogType = 'Create';
        },
        handleUpdate(row) {
            this.dialogData = Object.assign({}, row);
            this.dialogFormVisible = true;
            this.dialogType = 'Update';
        },
        createTask() {
            this.dialogFormVisible = false;

            createTask({
                concurrency: this.dialogData.concurrency,
                name: this.dialogData.name,
                task_config: JSON.parse(this.dialogData.task_config) }
            ).then(response => {
                this.$message({
                    showClose: true,
                    message: 'Task Settings Created',
                    type: 'success'
                });
                this.getList();
            });
        },
        updateTask() {
            this.dialogFormVisible = false;

            updateTask(this.dialogData.uuid, {
                concurrency: this.dialogData.concurrency,
                name: this.dialogData.name,
                task_config: JSON.parse(this.dialogData.task_config) }
            ).then(response => {
                this.$message({
                    showClose: true,
                    message: 'Task Settings Updated',
                    type: 'success'
                });
                this.getList();
            });
        },
        handleDialogConfirm() {
            this.$refs.dialogForm.validate(valid => {
                if (valid) {
                    if (this.dialogType === 'Create') {
                        this.createTask();
                    } else {
                        this.updateTask();
                    }
                } else {
                    return false;
                }
            });
        },
        sortChange(data) {
            const { prop, order } = data;
            console.log(prop);
            console.log(order);
        }
    }
};
</script>
