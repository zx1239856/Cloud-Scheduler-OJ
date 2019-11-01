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
      <el-table-column label="Tag" width="100" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.Tag }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Docker Version" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.DockerVersion }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Entrypoint" min-width="120" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.Entrypoint }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Exposed Ports" min-width="150" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.ExposedPorts }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Volumes" min-width="100" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.Volumes }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Created" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ new Date(scope.row.Created).toLocaleString() }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Action" width="100" align="center">
        <template slot-scope="{row}">
          <el-button type="danger" size="small" icon="el-icon-delete" :disabled="row.name == 'cloud-scheduler-userspace'" @click="handleDelete(row)" />
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getRepository()" />

    <el-dialog
      title="Warning"
      :visible.sync="deleteDialogVisible"
      width="30%"
    >
      <span>Are you sure to delete Image {{ Repo + ':' + selectedData.Tag }}?</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible=false">Cancel</el-button>
        <el-button type="danger" @click="deleteImage">Delete</el-button>
      </span>
    </el-dialog>

  </div>
</template>

<script>
import { getRepository, deleteImage } from '@/api/registry';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'RepositoryInfos',
    components: { Pagination },
    directives: { waves },
    data() {
        return {
            Repo: '',
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
    created() {
        this.Repo = this.$route.query.repo;
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
        handleDelete(row) {
            this.selectedData = Object.assign({}, row);
            this.deleteDialogVisible = true;
        },
        deleteImage() {
            this.deleteDialogVisible = false;
            this.$message({
                showClose: true,
                message: this.Repo,
                type: 'success'
            });
            deleteImage(
                this.Repo,
                this.selectedData.Tag
            ).then(response => {
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
