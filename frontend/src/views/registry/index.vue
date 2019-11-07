<template>
  <div class="app-container">
    <div class="filter-container" align="right">
      <el-button class="filter-item" style="margin: 10px;" type="primary" icon="el-icon-plus" @click="handleUpload()">
        New Image
      </el-button>
      <el-button icon="el-icon-time" type="info" @click="handleUploadHistory()">
        Upload Status
      </el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="4">
        <el-table
          :key="tableKey"
          v-loading="listLoading"
          :data="list"
          border
          fit
          highlight-current-row
          style="width: 100%;"
        >
          <el-table-column label="Repository" min-width="100" align="center">
            <template slot-scope="scope">
              <span class="link-type" @click="handleImageInfo(scope.row)">{{ scope.row.Repo }}</span>
            </template>
          </el-table-column>
        </el-table>
      </el-col>
      <el-col :span="20">
        <el-table
          :key="subTableKey"
          v-loading="subListLoading"
          :data="subList"
          fit
          highlight-current-row
          style="width: 100%;"
        >
          <el-table-column label="Tag" width="100" align="center">
            <template slot-scope="scope2">
              <span>{{ scope2.row.Tag }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Docker Version" min-width="200" align="center">
            <template slot-scope="scope2">
              <span>{{ scope2.row.DockerVersion }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Entrypoint" min-width="120" align="center">
            <template slot-scope="scope2">
              <span>{{ scope2.row.Entrypoint }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Exposed Ports" min-width="150" align="center">
            <template slot-scope="scope2">
              <span>{{ scope2.row.ExposedPorts }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Volumes" min-width="100" align="center">
            <template slot-scope="scope2">
              <span>{{ scope2.row.Volumes }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Created" width="200" align="center">
            <template slot-scope="scope2">
              <span>{{ new Date(scope2.row.Created).toLocaleString() }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Action" width="100" align="center">
            <template slot-scope="{row}">
              <el-button type="danger" size="small" icon="el-icon-delete" :disabled="row.name === 'cloud-scheduler-userspace'" @click="handleDelete(row)" />
            </template>
          </el-table-column>
        </el-table>
      </el-col>
    </el-row>

    <div style="text-align: center;">
      <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getRepositories()" />
    </div>

    <el-dialog :title="dialogType" :visible.sync="dialogFormVisible">
      <el-form ref="dialogForm" :model="dialogData" enctype="multipart/form-data" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;">
        <el-form-item label="file" prop="file">
          <el-upload
            action="no"
            multiple
            :http-request="getImage"
          >
            <i class="el-icon-plus" />
          </el-upload>
        </el-form-item>
        <el-form-item label="Repo Name" prop="repo">
          <el-input ref="inputPath" v-model="dialogData.repo" @keyup.enter.native="handleDialogConfirm" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible=false">
          Cancel
        </el-button>
        <el-button :loading="dialogLoading" type="primary" @click="handleDialogConfirm()">
          Upload
        </el-button>
      </div>
    </el-dialog>

    <el-dialog
      title="Warning"
      :visible.sync="deleteDialogVisible"
      width="30%"
    >
      <span>Are you sure to delete Image {{ currentRepo + ':' + selectedData.Tag }}?</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible=false">Cancel</el-button>
        <el-button :loading="deleteDialogLoading" type="danger" @click="deleteImage()">Delete</el-button>
      </span>
    </el-dialog>

    <el-dialog title="Upload Status" :visible.sync="dialogHistoryVisible" :before-close="handleHistoryClose">
      <el-container>
        <el-header>
          <div class="filter-container" align="right">
            <el-button icon="el-icon-time" type="info" @click="handleUploadHistory()">
              Refresh
            </el-button>
          </div>
        </el-header>
        <el-main>
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
              <el-table-column label="File Name" min-width="100" align="center" height="10">
                <template slot-scope="scope">
                  <span>{{ scope.row.name }}</span>
                </template>
              </el-table-column>
              <el-table-column label="Status" class-name="status-col" min-width="100" align="center">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.status | statusFilter" @click="handleError(scope.row)">
                    {{ statusMap[scope.row.status] }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-main>
        <div style="text-align: center;">
          <pagination v-show="historyList.total>0" :total="historyList.total" :page.sync="historyList.listQuery.page" :limit.sync="historyList.listQuery.limit" :page-sizes="historyList.pageSizes" @pagination="getHistoryList()" />
        </div>
      </el-container>
    </el-dialog>
  </div>
</template>

<script>
import { getRepositories, uploadImage, getRepository, deleteImage, getImageList } from '@/api/registry';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'RepositoryList',
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
            currentRepo: '',
            dialogType: 'Upload',
            dialogFormVisible: false,
            dialogLoading: false,
            deleteDialogLoading: false,
            deleteDialogVisible: false,
            dialogHistoryVisible: false,
            tableKey: 0,
            subTableKey: 0,
            list: null,
            subList: null,
            total: 0,
            listLoading: true,
            subListLoading: true,
            pageSizes: [25],
            listQuery: {
                page: 1,
                limit: 25
            },
            selectedData: {
                Repo: '',
                Tag: ''
            },
            dialogData: {
                file: [],
                repo: ''
            },
            historyList: {
                tableKey: 0,
                list: null,
                total: 0,
                listLoading: true,
                pageSizes: [10, 25],
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
    created() {
        this.getRepositoryList();
        this.subListLoading = false;
    },
    methods: {
        getTagList() {
            this.subListLoading = true;
            getRepository(this.currentRepo).then(response => {
                this.subList = response.payload.entity;
            }).finally(() => {
                this.subListLoading = false;
            });
        },
        getRepositoryList() {
            this.listLoading = true;
            getRepositories(this.listQuery).then(response => {
                this.list = response.payload.entity;
                this.total = response.payload.count;
            }).finally(() => {
                this.listLoading = false;
            });
        },
        getHistoryList() {
            this.historyList.listLoading = true;
            getImageList(this.historyList.listQuery).then(response => {
                this.historyList.list = response.payload.entry;
                this.historyList.total = response.payload.count;
            }).finally(() => {
                this.historyList.listLoading = false;
            });
        },
        handleImageInfo(row) {
            this.currentRepo = row.Repo;
            this.getTagList();
        },
        handleUpload() {
            this.dialogData.file.splice(0, this.dialogData.file.length);
            this.dialogData.repo = '';
            this.dialogFormVisible = true;
            this.dialogType = 'Upload';
        },
        uploading() {
            this.dialogLoading = true;
            var formData = new FormData();
            for (var f of this.dialogData.file) {
                formData.append('file[]', f);
            }
            formData.append('repo', this.dialogData.repo);

            uploadImage(formData).then(response => {
                this.$message({
                    showClose: true,
                    message: 'Image Uploaded',
                    type: 'success'
                });
            }).finally(() => {
                this.dialogLoading = false;
                this.dialogFormVisible = false;
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
                    }
                } else {
                    return false;
                }
            });
        },
        getImage(item) {
            this.dialogData.file.push(item.file);
        },
        handleDelete(row) {
            this.selectedData = Object.assign({}, row);
            this.deleteDialogVisible = true;
        },
        deleteImage() {
            this.deleteDialogLoading = true;
            deleteImage(
                this.currentRepo,
                this.selectedData.Tag
            ).then(response => {
                this.$message({
                    showClose: true,
                    message: 'Deleted!',
                    type: 'success'
                });
                this.getTagList();
            }).finally(() => {
                this.deleteDialogLoading = false;
                this.deleteDialogVisible = false;
            });
        },
        handleUploadHistory() {
            this.getHistoryList();
            this.dialogHistoryVisible = true;
        },
        handleHistoryClose(done) {
            if (this.currentRepo !== '') {
                this.getTagList();
            }
            done();
        }
    }
};
</script>

<style lang="scss" scoped>
.link-type,
.link-type:focus {
  color: #337ab7;
  cursor: pointer;

  &:hover {
    color: rgb(32, 160, 255);
  }
}
</style>
