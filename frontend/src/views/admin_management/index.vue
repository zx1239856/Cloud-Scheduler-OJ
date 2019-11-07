<template>
  <div class="app-container">
    <div class="filter-container" align="right">
      <el-button class="filter-item" style="margin: 20px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        New Admin
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
      <el-table-column label="UUID" width="300" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.uuid }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Username" width="150" align="center">
        <template slot-scope="{row}">
          <span>{{ row.username }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Email" min-width="120" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.email }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Created Time" width="220" align="center">
        <template slot-scope="scope">
          <span>{{ new Date(scope.row.create_time).toLocaleString() }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" width="230" class-name="small-padding fixed-width">
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
        <el-form-item label="Username" prop="username">
          <el-input v-if="dialogTitle==='Create'" ref="inputUsername" v-model="dialogData.username" />
          <span v-else>{{ dialogData.username }}</span>
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input ref="inputEmail" v-model="dialogData.email" @keyup.enter.native="handleDialogConfirm" />
        </el-form-item>
        <el-form-item v-if="dialogTitle!=='Create'" label="Reset Password" prop="password_reset">
          <el-checkbox v-model="dialogData.password_reset">Reset Password</el-checkbox>
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
      <span>Are you sure to delete this admin account?</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button :loading="deleteDialogLoading" type="danger" @click="handleDeleteDialogConfirm">Delete</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getAdminList, createAdmin, updateAdmin, deleteAdmin } from '@/api/admin';
import { validateEmail } from '@/utils/validate';
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'TaskSettings',
    components: { Pagination },

    data() {
        const emailValidator = (rule, value, callback) => {
            if (!validateEmail(value)) {
                callback(new Error('Invalid email'));
            } else {
                callback();
            }
        };
        const usernameValidator = (rule, value, callback) => {
            if (this.dialogTitle === 'Create' && value.length === 0) {
                return callback(new Error('This is required'));
            } else {
                return callback();
            }
        };
        return {
            dialogData: {
                username: '',
                email: '',
                uuid: '',
                password_reset: false
            },
            dialogTitle: 'Create',
            dialogVisible: false,
            dialogLoading: false,
            deleteDialogLoading: false,
            deleteDialogVisible: false,
            tableKey: 0,
            list: null,
            total: 0,
            listLoading: true,

            listQuery: {
                page: 1,
                limit: 25,
                pageSizes: [25]
            },
            dialogRules: {
                username: [{
                    required: true,
                    trigger: 'change',
                    validator: usernameValidator
                }],
                email: [{
                    required: true,
                    trigger: 'change',
                    validator: emailValidator
                }]
            }
        };
    },
    created() {
        this.getList();
    },
    methods: {
        getList() {
            this.listLoading = true;

            getAdminList(this.listQuery.page).then(response => {
                this.list = response.payload.entry;
                this.total = response.payload.count;
            }).finally(() => {
                this.listLoading = false;
            });
        },
        handleDeleteDialogConfirm() {
            this.deleteDialogLoading = true;
            deleteAdmin(this.dialogData.uuid)
                .then(response => {
                    this.$message({
                        message: 'Successfully Deleted',
                        type: 'success'
                    });
                    this.getList();
                })
                .finally(() => {
                    this.deleteDialogVisible = false;
                    this.deleteDialogLoading = false;
                });
        },
        handleCreate() {
            this.dialogTitle = 'Create';
            this.dialogVisible = true;
            this.dialogData = {
                username: '',
                email: '',
                uuid: ''
            };
            this.$nextTick(() => {
                this.$refs.inputUsername.focus();
            });
        },
        handleUpdate(row) {
            this.dialogTitle = 'Update';
            this.dialogData = Object.assign({}, row);
            this.dialogVisible = true;

            this.$nextTick(() => {
                this.$refs.inputEmail.focus();
                this.$refs.dialogForm.validate(() => {});
            });
        },
        handleDelete(row) {
            this.deleteDialogVisible = true;
            this.dialogData = Object.assign({}, row);
        },
        handleDialogConfirm() {
            this.$refs.dialogForm.validate(valid => {
                if (!valid) {
                    return false;
                }
                this.dialogLoading = true;
                if (this.dialogTitle === 'Create') {
                    // create
                    createAdmin(this.dialogData.username, this.dialogData.email)
                        .then(response => {
                            this.$message({
                                message: 'Successfully Created',
                                type: 'success'
                            });
                            this.getList();
                        })
                        .finally(() => {
                            this.dialogVisible = false;
                            this.dialogLoading = false;
                        });
                } else {
                    // update
                    updateAdmin(this.dialogData.uuid, this.dialogData.email, this.dialogData.password_reset)
                        .then(response => {
                            if (response.message.includes('failed')) {
                                this.$message.error(response.message);
                            } else {
                                this.$message({
                                    message: 'Successfully Updated',
                                    type: 'success'
                                });
                            }
                            this.getList();
                        })
                        .finally(() => {
                            this.dialogVisible = false;
                            this.dialogLoading = false;
                        });
                }
            });
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
