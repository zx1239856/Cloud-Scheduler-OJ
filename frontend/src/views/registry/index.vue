<template>
  <div class="app-container">
    <div class="filter-container" align="right">
      <el-button class="filter-item" style="margin: 10px;" type="primary" icon="el-icon-plus" @click="handleUpload">
        New Image
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
      <el-table-column label="Repository" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.Repo }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" width="150" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-row>
            <el-button type="primary" size="mini" @click="handleImageInfo(row)">
              Images
            </el-button>
          </el-row>
        </template>
      </el-table-column>
    </el-table>
    <el-drawer
      :title="currentRepo"
      :visible.sync="tableShow"
      direction="rtl"
      size="75%"
    >
      <el-table
        :key="subTableKey"
        v-loading="subListLoading"
        :data="subList"
        border
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
            <el-button type="danger" size="small" icon="el-icon-delete" :disabled="row.name == 'cloud-scheduler-userspace'" @click="handleDelete(row)" />
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>

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
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible=false">
          Cancel
        </el-button>
        <el-button type="primary" @click="handleDialogConfirm()">
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
        <el-button type="danger" @click="deleteImage()">Delete</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getRepositories, uploadImage, getRepository, deleteImage } from '@/api/registry';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'RepositoryList',
    components: { Pagination },
    directives: { waves },
    data() {
        return {
            currentRepo: '',
            tableShow: false,
            dialogType: 'Upload',
            dialogFormVisible: false,
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
            deleteDialogVisible: false,
            selectedData: {
                Repo: '',
                Tag: ''
            },
            dialogData: {
                file: []
            },
            dialogRules: {
                repo: [{
                    required: true,
                    message: 'Target Repository is required',
                    trigger: 'change'
                }],
                tag: [{
                    required: true,
                    message: 'Tag Version is required',
                    trigger: 'change'
                }]
            }
        };
    },
    created() {
        this.getRepositoryList();
    },
    methods: {
        getTagList() {
            this.subListLoading = true;
            getRepository(this.currentRepo).then(response => {
                this.subList = response.payload.entity;
                this.subListLoading = false;
            });
        },
        getRepositoryList() {
            this.listLoading = true;
            getRepositories(this.listQuery).then(response => {
                this.list = response.payload.entity;
                this.total = response.payload.count;
                this.listLoading = false;
            });
        },
        handleImageInfo(row) {
            this.tableShow = true;
            this.currentRepo = row.Repo;
            this.getTagList();
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

            uploadImage(formData).then(response => {
                this.$message({
                    showClose: true,
                    message: 'File Uploading',
                    type: 'success'
                });
                this.getRepositoryList();
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
            this.deleteDialogVisible = false;
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
            });
        }
    }
};
</script>
