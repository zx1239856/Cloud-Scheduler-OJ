<template>
  <div class="app-container">
    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="UUID" width="300" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.uuid }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Settings" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.settings.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="User" align="center" min-width="150">
        <template slot-scope="scope">
          <span>{{ scope.row.user }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Created Time" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ new Date(scope.row.create_time).toLocaleString() }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Status" class-name="status-col" width="150" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusTypeFilter">
            {{ row.status | statusFilter }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" width="150" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="danger" size="small" icon="el-icon-delete" @click="handleDelete(row)">
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getList" />

    <el-dialog
      title="Warning"
      :visible.sync="deleteDialogVisible"
      width="30%"
    >
      <span>Are you sure to delete this task?</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="deleteTask">Delete</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getTaskList, deleteTask } from '@/api/task';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'Task',
    components: { Pagination },
    directives: { waves },
    filters: {
        statusTypeFilter(status) {
            const statusTypeMap = {
                '0': 'info',
                '1': '',
                '2': 'success',
                '3': 'danger',
                '4': 'info',
                '5': 'warning',
                '6': 'danger'
            };
            return statusTypeMap[status];
        },
        statusFilter(status) {
            const statusMap = {
                '0': 'Scheduled',
                '1': 'Running',
                '2': 'Succeeded',
                '3': 'Failed',
                '4': 'Deleting',
                '5': 'Pending',
                '6': 'TLE'
            };
            return statusMap[status];
        }
    },
    data() {
        return {
            tableKey: 0,
            list: null,
            total: 0,
            listLoading: true,
            pageSizes: [25],
            listQuery: {
                page: 1,
                limit: 25
            },
            rules: {
                type: [{ required: true, message: 'type is required', trigger: 'change' }],
                timestamp: [{ type: 'date', required: true, message: 'timestamp is required', trigger: 'change' }],
                title: [{ required: true, message: 'title is required', trigger: 'blur' }]
            },
            selectedData: {
                uuid: ''
            },
            deleteDialogVisible: false
        };
    },
    created() {
        this.polling = window.setInterval(this.getList, 3 * 1000);
        this.getList();
    },
    beforeDestroy() {
        clearInterval(this.polling);
    },
    methods: {
        getList() {
            getTaskList(this.listQuery.page).then(response => {
                this.list = response.payload.entry;
                this.total = response.payload.count;
                this.listLoading = false;
            }).catch(() => {
                this.listLoading = false;
            });
        },
        handleDelete(row) {
            this.selectedData = Object.assign({}, row);
            this.deleteDialogVisible = true;
        },
        deleteTask() {
            this.deleteDialogVisible = false;
            deleteTask(this.selectedData.uuid).then(response => {
                this.$message({
                    showClose: true,
                    message: 'Task Deleted',
                    type: 'success'
                });
            });
        }
    }
};
</script>
