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
      <el-table-column label="Tag" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.Tag }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Size" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.Size }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Layers" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.Layers }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Created" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ new Date(scope.row.Created).toLocaleString() }}</span>
        </template>
      </el-table-column>
      <el-table-column width="100" align="center">
        <template slot-scope="{row}">
          <el-button type="danger" size="small" icon="el-icon-delete" :disabled="row.name == 'cloud-scheduler-userspace'" @click="handleDelete(row)" />
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getRepository" />

    <el-dialog :title="dialogType" :visible.sync="dialogFormVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="dialogData" enctype="multipart/form-data" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;">
        <el-form-item label="file" prop="file">
          <el-upload
            action="no"
            multiple
            :http-request="getImage"
          >
            <i class="el-icon-plus" />
          </el-upload>
        </el-form-item>
        <el-form-item label="Repository" prop="repo">
          <el-input v-model="dialogData.repo" />
        </el-form-item>
        <el-form-item label="Tag" prop="tag">
          <el-input v-model="dialogData.tag" />
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

    <el-dialog
      title="Warning"
      :visible.sync="deleteDialogVisible"
      width="30%"
    >
      <span>Are you sure to delete Image {{ selectedData.Repo }}?</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="deleteImage">Delete</el-button>
      </span>
    </el-dialog>

  </div>
</template>

<script>
import { getRepository, uploadImage, deleteImage } from '@/api/registry';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'RepositoryInfos',
    components: { Pagination },
    directives: { waves },
    data() {
        return {
            Repo: '',
            dialogType: 'Upload',
            dialogFormVisible: false,
            deleteDialogVisible: false,
            selectedData: {
                Repo: '',
                Tag: ''
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
                repo: '',
                tag: ''
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
    // computed: {
    //     ...mapGetters([
    //         'permission'
    //     ])
    // },
    created() {
        this.getRepositoryList();
    },
    methods: {
        getRepositoryList() {
            this.listLoading = true;
            getRepository(this.$route.query.repo).then(response => {
                this.list = response.payload.entity;
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

            formData.append('file', this.dialogData.file);

            uploadImage(formData, this.dialogData.repo, this.dialogData.tag).then(response => {
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
                    } else {
                        //
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
            this.$message({
                showClose: true,
                message: this.selectedData.name,
                type: 'success'
            });
            deleteImage({
                name: this.selectedData.name
            }).then(response => {
                this.$message({
                    showClose: true,
                    message: 'Deleted!',
                    type: 'success'
                });
                this.getRepositoryList();
            });
        }
    }
};
</script>
