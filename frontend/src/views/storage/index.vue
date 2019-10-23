<template>
  <div class="app-container">
    <div class="filter-container" align="right">
      <el-button class="filter-item" style="margin: 10px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        Create PVC
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
      <el-table-column label="PVC Name" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Capacity" min-width="300" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.capacity }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Create Time" min-width="300" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.time }}</span>
        </template>
      </el-table-column>
      <el-table-column width="100" align="center">
        <template slot-scope="{row}">
          <el-button type="danger" size="small" icon="el-icon-delete" @click="handleDelete(row)" />
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getList" />

    <el-dialog :title="dialogType" :visible.sync="dialogFormVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="dialogData" enctype="multipart/form-data" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;">
        <el-form-item label="name" prop="name">
          <el-input v-model="dialogData.name" />
        </el-form-item>
        <el-form-item label="capacity" prop="capacity">
          <el-input v-model="dialogData.capacity" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Cancel
        </el-button>
        <el-button type="primary" @click="handleDialogConfirm">
          Create
        </el-button>
      </div>
    </el-dialog>

    <el-dialog
      title="Warning"
      :visible.sync="deleteDialogVisible"
      width="30%"
    >
      <span>Are you sure to delete PVC {{ selectedData.name }}?</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="deletePVC">Delete</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getPVCList, createPVC, deletePVC } from '@/api/storage';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination
import { mapGetters } from 'vuex';

export default {
    name: 'PVC',
    components: { Pagination },
    directives: { waves },

    data() {
        return {
            dialogType: 'Create',
            dialogFormVisible: false,
            deleteDialogVisible: false,
            selectedData: {
                name: ''
            },
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
                name: '',
                capacity: ''
            },
            dialogRules: {
                name: [{
                    required: true,
                    message: 'pvc name is required',
                    trigger: 'change'
                }],
                capacity: [{
                    required: true,
                    message: 'capacity is required',
                    trigger: 'change'
                }]
            }
        };
    },
    computed: {
        ...mapGetters([
            'permission'
        ])
    },
    created() {
        this.getList();
    },
    methods: {
        getList() {
            this.listLoading = true;
            getPVCList(this.listQuery.page).then(response => {
                this.list = response.payload.entry;
                this.total = response.payload.count;
                this.listLoading = false;
            });
        },
        handleCreate() {
            this.dialogFormVisible = true;
            this.dialogType = 'Create';
        },
        handleDialogConfirm() {
            this.$refs.dialogForm.validate(valid => {
                if (valid) {
                    if (this.dialogType === 'Create') {
                        this.createPVC();
                    } else {
                        //
                    }
                } else {
                    return false;
                }
            });
        },
        createPVC() {
            this.dialogFormVisible = false;
            createPVC({
                name: this.dialogData.name,
                capacity: this.dialogData.capacity
            }).then(response => {
                this.$message({
                    showClose: true,
                    message: 'Created!',
                    type: 'success'
                });
                this.getList();
            });
        },
        handleDelete(row) {
            this.selectedData = Object.assign({}, row);
            this.deleteDialogVisible = true;
        },
        deletePVC() {
            this.$message({
                showClose: true,
                message: this.selectedData.name,
                type: 'success'
            });
            deletePVC({
                name: this.selectedData.name
            }).then(response => {
                this.$message({
                    showClose: true,
                    message: 'Deleted!',
                    type: 'success'
                });
                this.getList();
            });
        }
    }
};
</script>
