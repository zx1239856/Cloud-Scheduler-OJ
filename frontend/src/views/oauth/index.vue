<template>
  <div class="app-container">
    <div align="right">
      <el-button style="margin: 20px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        New App
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
      <el-table-column label="Model" width="250" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.model }}</span>
        </template>
      </el-table-column>
      <el-table-column label="ID" width="100" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.pk }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Name" min-width="100" align="center">
        <template slot-scope="scope">
          <span class="link-type" @click="handleDisplayDetail(scope.row)">{{ scope.row.fields.name }}</span>
        </template>
      </el-table-column>
      <!-- <el-table-column label="Client ID" width="350" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.fields.client_id }}</span>
        </template>
      </el-table-column> -->
      <el-table-column label="Created" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ new Date(scope.row.fields.created).toLocaleString() }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Updated" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ new Date(scope.row.fields.updated).toLocaleString() }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="200" align="center">
        <template slot-scope="{row}">
          <el-button plain type="warning" size="small" icon="el-icon-edit" @click="handleUpdate(row)">
            Edit
          </el-button>
          <el-button plain type="danger" size="small" icon="el-icon-delete" @click="handleDelete(row)">
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="text-align: center;">
      <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="listQuery.pageSizes" @pagination="getList" />
    </div>

    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="dialogData" enctype="multipart/form-data" label-position="left" label-width="200px" style="width: 500px; margin-left:50px;">
        <el-form-item label="Name" prop="name">
          <el-input ref="inputName" v-model="dialogData.name" />
        </el-form-item>
        <el-form-item label="Redirect URI" prop="redirect_uri">
          <el-input v-model="dialogData.redirect_uri" @keyup.enter.native="handleDialogConfirm" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">
          Cancel
        </el-button>
        <el-button :loading="dialogLoading" type="primary" @click="handleDialogConfirm">
          {{ dialogTitle }}
        </el-button>
      </div>
    </el-dialog>

    <el-dialog
      title="Warning"
      :visible.sync="deleteDialogVisible"
      width="30%"
    >
      <span>Are you sure to delete this app?</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button :loading="deleteDialogLoading" type="danger" @click="handleDeleteConfirm">Delete</el-button>
      </span>
    </el-dialog>

    <el-dialog
      title="Detail"
      :visible.sync="detailDialogVisible"
      class="detail-dialog"
    >

      <el-form v-if="selectedRowData" enctype="multipart/form-data" label-position="left" label-width="200px" style="width: 1000px; margin-left: 50px;">
        <el-form-item label="ID">
          <span>{{ selectedRowData.pk }}</span>
        </el-form-item>
        <el-form-item label="Model">
          <span>{{ selectedRowData.model }}</span>
        </el-form-item>
        <el-form-item label="Name">
          <span>{{ selectedRowData.fields.name }}</span>
        </el-form-item>
        <el-form-item label="Client ID">
          <span>{{ selectedRowData.fields.client_id }}</span>
        </el-form-item>
        <el-form-item label="Redirect URI">
          <a :href="selectedRowData.fields.redirect_uris.split(' ')[0]" target="_blank">
            <span class="link-type">{{ selectedRowData.fields.redirect_uris.split(' ')[0] }}</span>
          </a>
        </el-form-item>
        <el-form-item label="Client Type">
          <span>{{ selectedRowData.fields.client_type }}</span>
        </el-form-item>
        <el-form-item label="Authorization Grant Type">
          <span>{{ selectedRowData.fields.authorization_grant_type }}</span>
        </el-form-item>
        <el-form-item label="Client Secret">
          <div style="width: 400px;">{{ selectedRowData.fields.client_secret }}</div>
        </el-form-item>
        <el-form-item label="Skip Authorization">
          <div style="width: 400px;">{{ selectedRowData.fields.skip_authorization }}</div>
        </el-form-item>
        <el-form-item label="Created">
          <span>{{ new Date(selectedRowData.fields.created).toLocaleString() }}</span>
        </el-form-item>
        <el-form-item label="Updated">
          <span>{{ new Date(selectedRowData.fields.updated).toLocaleString() }}</span>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script>
import { getOAuthApp, createOAuthApp, updateOAuthApp, deleteOAuthApp } from '@/api/oauth';
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'OAuth',
    components: { Pagination },
    data() {
        return {
            dialogLoading: false,
            deleteDialogLoading: false,
            dialogData: {
                uuid: 0,
                name: '',
                redirect_uri: ''
            },
            listQuery: {
                page: 1,
                limit: 25,
                pageSizes: [25]
            },
            selectedRowData: null,
            total: 0,
            dialogTitle: 'Create',
            dialogVisible: false,
            deleteDialogVisible: false,
            detailDialogVisible: false,
            tableKey: 0,
            list: [],
            dialogRules: {
                name: [{
                    required: true,
                    message: 'This is required',
                    trigger: 'blur'
                }],
                redirect_uri: [{
                    required: true,
                    message: 'This is required',
                    trigger: 'blur'
                }]
            },
            listLoading: true
        };
    },
    created() {
        this.getList();
    },
    methods: {
        getList() {
            getOAuthApp(this.listQuery.page).then(response => {
                this.list = response.payload.entry;
                this.total = response.payload.count;
            }).finally(() => {
                this.listLoading = false;
            });
        },
        handleCreate() {
            this.dialogTitle = 'Create';
            this.dialogData = {
                uuid: 0,
                name: '',
                redirect_uri: ''
            };
            this.dialogVisible = true;
            this.$nextTick(() => {
                this.$refs.inputName.focus();
            });
        },
        handleDeleteConfirm() {
            this.deleteDialogLoading = true;
            deleteOAuthApp(this.selectedRowData.pk)
                .then(response => {
                    this.$message({
                        message: 'Successfully Deleted',
                        type: 'success'
                    });
                    this.getList();
                }).finally(() => {
                    this.deleteDialogLoading = false;
                    this.deleteDialogVisible = false;
                });
        },
        handleDisplayDetail(row) {
            this.selectedRowData = Object.assign({}, row);
            this.detailDialogVisible = true;
        },
        handleUpdate(row) {
            this.dialogTitle = 'Update';
            this.dialogVisible = true;
            this.dialogData = {
                uuid: row.pk,
                name: row.fields.name,
                redirect_uri: row.fields.redirect_uris.split(' ')[0]
            };
            this.$nextTick(() => {
                this.$refs.inputName.focus();
            });
        },
        handleDelete(row) {
            this.deleteDialogVisible = true;
            this.selectedRowData = Object.assign({}, row);
        },
        handleDialogConfirm() {
            this.$refs.dialogForm.validate(valid => {
                if (!valid) {
                    return false;
                }
                this.dialogLoading = true;
                this.dialogVisible = false;
                if (this.dialogTitle === 'Create') {
                    // create
                    createOAuthApp(this.dialogData.name, [this.dialogData.redirect_uri])
                        .then(response => {
                            this.$message({
                                message: 'Successfully Created',
                                type: 'success'
                            });
                            this.getList();
                        }).finally(() => {
                            this.dialogLoading = false;
                        });
                } else {
                    // update
                    updateOAuthApp(this.dialogData.uuid, this.dialogData.name, [this.dialogData.redirect_uri])
                        .then(response => {
                            this.$message({
                                message: 'Successfully Updated',
                                type: 'success'
                            });
                            this.getList();
                        }).finally(() => {
                            this.dialogLoading = false;
                        });
                }
            });
        }
    }
};
</script>

<style lang="scss">
.link-type,
.link-type:focus {
  color: #337ab7;
  cursor: pointer;

  &:hover {
    color: rgb(32, 160, 255);
  }
}

.detail-dialog{
    > div{
        margin-top: 5vh !important;
    }
    .el-form-item {
        margin-bottom: 0px;
    }
    span{
        width: 800px;
    }
}
</style>
