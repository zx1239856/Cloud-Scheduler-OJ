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
      <el-table-column label="Number of Tags" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.NumberOfTags }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Size" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.SizeOfRepository }}</span>
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

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getRepositories" />

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
        <!-- <el-form-item label="Repository" prop="repo">
          <el-input v-model="dialogData.repo" />
        </el-form-item>
        <el-form-item label="Tag" prop="tag">
          <el-input v-model="dialogData.tag" />
        </el-form-item> -->
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
import { getRepositories, uploadImage } from '@/api/registry';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'RepositoryList',
    components: { Pagination },
    directives: { waves },
    data() {
        return {
            dialogType: 'Upload',
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
                file: []
            },
            dialogRules: {
                // pvc: [{
                //     required: true,
                //     message: 'concurrency is required',
                //     trigger: 'change'
                // }],
                // path: [{
                //     required: true,
                //     message: 'path is required',
                //     trigger: 'change'
                // }]
            }
        };
    },
    created() {
        this.getRepositoryList();
    },
    methods: {
        getRepositoryList() {
            this.listLoading = true;
            getRepositories(this.listQuery).then(response => {
                this.list = response.payload.entity;
                this.total = response.payload.count;
                this.listLoading = false;
            });
        },
        handleImageInfo(row) {
            const routeData = this.$router.resolve({ name: 'image', query: { repo: row.Repo }});
            window.open(routeData.href);
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
        }
    }
};
</script>
