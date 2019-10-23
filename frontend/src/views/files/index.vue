<template>
  <div class="app-container">
    <div class="filter-container" align="right">
      <el-button class="filter-item" style="margin: 10px;" type="primary" icon="el-icon-refresh" @click="handleReupload">
        Re-upload
      </el-button>
      <el-button class="filter-item" style="margin: 10px;" type="primary" icon="el-icon-upload2" @click="handleUpload">
        Upload File
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
      <el-table-column label="File Name" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Target PVC" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.pvc }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Target Path" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.path }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Upload Time" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.time }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Status" class-name="status-col" width="200" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ statusMap[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getList" />

    <el-dialog :title="dialogType" :visible.sync="dialogFormVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="dialogData" enctype="multipart/form-data" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;">
        <el-form-item label="file" prop="file">
          <el-upload
            action="no"
            multiple
            :http-request="getFile"
          >
            <i class="el-icon-plus" />
          </el-upload>
        </el-form-item>
        <el-form-item label="pvc" prop="pvc">
          <el-input v-model="dialogData.pvc" />
        </el-form-item>
        <el-form-item label="path" prop="path">
          <el-input v-model="dialogData.path" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Cancel
        </el-button>
        <el-button type="primary" @click="handleDialogConfirm">
          Upload
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getFileList, uploadFile, reuploadFile } from '@/api/storage';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination
import { mapGetters } from 'vuex';

export default {
    name: 'FileList',
    components: { Pagination },
    directives: { waves },
    filters: {
        statusFilter(status) {
            const map = {
                0: 'warning',
                1: 'info',
                2: 'info',
                3: 'info',
                4: 'success',
                5: 'danger'
            };
            return map[status];
        }
    },
    data() {
        return {
            dialogType: 'Upload',
            dialogFormVisible: false,
            deleteDialogVisible: false,
            tableKey: 0,
            list: null,
            total: 0,
            listLoading: true,
            pageSizes: [25],
            listQuery: {
                page: 1,
                limit: 25
            },
            statusMap: {
                0: 'Pending',
                1: 'Caching',
                2: 'Cached',
                3: 'Uploading',
                4: 'Succeeded',
                5: 'Failed'
            },
            dialogData: {
                file: [],
                pvc: '',
                path: ''
            },
            dialogRules: {
                pvc: [{
                    required: true,
                    message: 'concurrency is required',
                    trigger: 'change'
                }],
                path: [{
                    required: true,
                    message: 'path is required',
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
            getFileList(this.listQuery).then(response => {
                this.list = response.payload.entry;
                this.total = response.payload.count;
                this.listLoading = false;
            });
        },
        handleUpload() {
            this.dialogFormVisible = true;
            this.dialogType = 'Upload';
        },
        uploading() {
            this.dialogFormVisible = false;
            var formData = new FormData();

            for (var f of this.dialogData.file) {
                formData.append('file[]', f);
            }

            formData.append('pvcName', this.dialogData.pvc);
            formData.append('mountPath', this.dialogData.path);

            uploadFile(formData).then(response => {
                this.$message({
                    showClose: true,
                    message: 'File Uploading',
                    type: 'success'
                });
                this.getList();
            });
        },
        handleDialogConfirm() {
            if (this.dialogData.file.length === 0) {
                this.$message({
                    showClose: true,
                    message: 'file required',
                    type: 'error'
                });
                return false;
            }
            this.$refs.dialogForm.validate(valid => {
                if (valid) {
                    if (this.dialogType === 'Upload') {
                        this.uploading();
                    } else {
                        //
                    }
                } else {
                    return false;
                }
            });
        },
        getFile(item) {
            this.dialogData.file.push(item.file);
        },
        handleReupload() {
            reuploadFile({}).then(response => {
                this.$message({
                    showClose: true,
                    message: 'File ReUploading',
                    type: 'success'
                });
                this.getList();
            });
        }
    }
};
</script>
