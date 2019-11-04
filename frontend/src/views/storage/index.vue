<template>
  <div class="app-container">
    <div class="filter-container" align="right">
      <el-button class="filter-item" style="margin: 10px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        Create PVC
      </el-button>
      <el-button icon="el-icon-time" type="info" @click="handleUploadHistory">
        Upload Log
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
    >
      <el-table-column label="Storage Name" min-width="140" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Capacity" width="100" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.capacity }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Access Mode" width="130" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.mode }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Create Time" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ new Date(scope.row.time).toLocaleString() }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Status" width="110" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.status }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" min-width="120" align="center">
        <template slot-scope="{row}">
          <el-button icon="el-icon-upload" type="primary" size="small" @click="handleUpload(row)">
            upload
          </el-button>
          <el-button type="danger" size="small" icon="el-icon-delete" :disabled="row.name == 'cloud-scheduler-userspace'" @click="handleDelete(row)" />
        </template>
      </el-table-column>
    </el-table>

    <div style="text-align: center;">
      <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getList" />
    </div>

    <el-dialog :title="dialogType" :visible.sync="dialogUploadVisible">
      <el-form ref="dialogForm" :model="dialogFileData" enctype="multipart/form-data" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;" @submit.native.prevent>
        <el-form-item label="file" prop="file">
          <el-upload
            ref="upload"
            action="no"
            multiple
            :on-remove="rmFile"
            :http-request="getFile"
          >
            <i class="el-icon-plus" />
          </el-upload>
        </el-form-item>
        <el-form-item label="path" prop="path">
          <el-input ref="inputPath" v-model="dialogFileData.path" @keyup.enter.native="handleUploadConfirm" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="handleUploadCancel">
          Cancel
        </el-button>
        <el-button type="primary" @click="handleUploadConfirm">
          Upload
        </el-button>
      </div>
    </el-dialog>
    <el-dialog title="Upload History" :visible.sync="dialogHistoryVisible">
      <div class="filter-container" align="right" style="margin-top:-25px; margin-bottom:10px">
        <el-button type="success" size="small" icon="el-icon-refresh" @click="handleReupload">
          Re-upload
        </el-button>
      </div>

      <div>
        <el-table
          :key="historyList.tableKey"
          v-loading="historyList.listLoading"
          :data="historyList.list"
          border
          fit
          highlight-current-row
          style="width: 100%;"
        >
          <el-table-column label="File Name" width="100" align="center" height="10">
            <template slot-scope="scope">
              <span>{{ scope.row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Storage" min-width="100" align="center">
            <template slot-scope="scope">
              <span>{{ scope.row.pvc }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Target Path" min-width="100" align="center">
            <template slot-scope="scope">
              <span>{{ scope.row.path }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Upload Time" min-width="150" align="center">
            <template slot-scope="scope">
              <span>{{ scope.row.time }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Status" class-name="status-col" width="110" align="center">
            <template slot-scope="scope">
              <el-tag :type="scope.row.status | statusFilter">
                {{ statusMap[scope.row.status] }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div style="text-align: center;">
          <pagination v-show="historyList.total>0" :total="historyList.total" :page.sync="historyList.listQuery.page" :limit.sync="historyList.listQuery.limit" :page-sizes="historyList.pageSizes" @pagination="getHistoryList" />
        </div>
      </div>
    </el-dialog>

    <el-dialog :title="dialogType" :visible.sync="dialogFormVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="dialogData" enctype="multipart/form-data" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;">
        <el-form-item label="name" prop="name">
          <el-input ref="inputName" v-model="dialogData.name" />
        </el-form-item>
        <el-form-item label="capacity" prop="capacity">
          <el-input v-model="dialogData.capacity" @keyup.enter.native="handleDialogConfirm" />
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
import { getPVCList, createPVC, deletePVC, uploadFile, getFileList, reuploadFile } from '@/api/storage';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination
import { mapGetters } from 'vuex';

export default {
    name: 'PVC',
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
            dialogType: 'Create',
            dialogFormVisible: false,
            deleteDialogVisible: false,
            dialogUploadVisible: false,
            dialogHistoryVisible: false,
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
            dialogFileData: {
                file: [],
                pvc: '',
                path: ''
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
            },
            historyList: {
                tableKey: 0,
                list: null,
                total: 0,
                listLoading: true,
                pageSizes: [25],
                listQuery: {
                    page: 1,
                    limit: 25
                }
            },
            statusMap: {
                0: 'Pending',
                1: 'Caching',
                2: 'Cached',
                3: 'Uploading',
                4: 'Succeeded',
                5: 'Failed'
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
        this.getHistoryList();
    },
    methods: {
        getList() {
            this.listLoading = true;
            getPVCList(this.listQuery).then(response => {
                this.list = response.payload.entry;
                this.total = response.payload.count;
                this.listLoading = false;
            });
        },
        handleCreate() {
            this.dialogFormVisible = true;
            this.dialogType = 'Create';
            this.$nextTick(() => {
                this.$refs.inputName.focus();
            });
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
            deletePVC({
                name: this.selectedData.name
            }).then(response => {
                this.$message({
                    showClose: true,
                    message: 'Deleted!',
                    type: 'success'
                });
                this.getList();
                this.deleteDialogVisible = false;
            });
        },
        handleUpload(row) {
            this.dialogFileData.file.splice(0, this.dialogFileData.file.length);
            this.dialogFileData.path = '';
            this.dialogUploadVisible = true;
            this.dialogType = 'Upload';
            this.dialogFileData.pvc = row.name;
            this.$nextTick(() => {
                this.$refs.inputPath.focus();
            });
        },
        handleUploadConfirm() {
            if (this.dialogFileData.file.length === 0) {
                this.$message({
                    showClose: true,
                    message: 'file required',
                    type: 'error'
                });
                return false;
            }
            this.$refs.upload.clearFiles();
            this.uploading();
        },
        getFile(item) {
            this.dialogFileData.file.push(item.file);
        },
        rmFile(file, fileList) {
            this.dialogFileData.file.forEach(function(item, index, arr) {
                if (item.name === file.name) {
                    arr.splice(index, 1);
                    throw new Error('EndIterative');
                }
            });
        },
        uploading() {
            this.dialogUploadVisible = false;
            var formData = new FormData();

            for (var f of this.dialogFileData.file) {
                formData.append('file[]', f);
            }

            formData.append('pvcName', this.dialogFileData.pvc);
            formData.append('mountPath', this.dialogFileData.path);

            uploadFile(formData).then(response => {
                this.$message({
                    showClose: true,
                    message: 'File Uploading',
                    type: 'success'
                });
                this.getHistoryList();
            });
        },
        handleUploadCancel() {
            this.dialogUploadVisible = false;
            this.dialogFileData.pvc = '';
        },
        getHistoryList() {
            this.historyList.listLoading = true;
            getFileList(this.historyList.listQuery).then(response => {
                this.historyList.list = response.payload.entry;
                this.historyList.total = response.payload.count;
                this.historyList.listLoading = false;
            });
        },
        handleUploadHistory() {
            this.getHistoryList();
            this.dialogHistoryVisible = true;
        },
        handleReupload() {
            reuploadFile({}).then(response => {
                this.$message({
                    showClose: true,
                    message: 'File ReUploading',
                    type: 'success'
                });
                this.getHistoryList();
            });
        },
        handleClear() {
            this.$message({
                showClose: true,
                message: 'Log Clear',
                type: 'success'
            });
        }
    }
};
</script>
