<template>
  <div class="container">
    <el-container>
      <el-aside width="300px">
        <div style="margin: 20px;">
          <span>
            Edit
          </span>
          <span style="float: right;">
            <el-tooltip class="item" effect="dark" content="New File" placement="top">
              <svg-icon icon-class="new_file" style="cursor:pointer; margin-left: 5px;" @click="handleCreateFile" />
            </el-tooltip>
            <el-tooltip class="item" effect="dark" content="New Directory" placement="top">
              <svg-icon icon-class="new_directory" style="cursor:pointer; margin-left: 5px;" @click="handleCreateDirectory" />
            </el-tooltip>
          </span>
        </div>
        <hr style="margin: 0px; border-top: 0.5px solid #dcdfe6;">
        <div style="overflow-y: scroll;">
          <el-tree id="el-tree" ref="tree" :props="props" :load="loadNode" lazy highlight-current @node-click="handleNodeClick">
            <span slot-scope="{ node }" class="custom-tree-node">
              <span>
                <span>
                  <svg-icon :icon-class="node.data.icon" />
                </span>
                <span style="margin-left: 5px;">{{ node.data.name }}</span>
              </span>
            </span>
          </el-tree>
          <context-menu
            class="right-menu"
            :target="contextMenuTarget"
            :show="contextMenuVisible"
            @update:show="(show) => contextMenuVisible = show"
          >
            <a href="javascript:;" style="display: flex;" @click="handleRename">
              <svg-icon icon-class="rename" />
              <span style="float: right; margin-left: 5px;">Rename</span>
            </a>
            <a href="javascript:;" style="display: flex;" @click="handleDelete">
              <svg-icon icon-class="delete" />
              <span style="float: right; margin-left: 5px;">Delete</span>
            </a>
          </context-menu>
        </div>
        <hr style="margin: 0px; border-top: 0.5px solid #dcdfe6;">
        <div style="text-align: center; margin: 20px;">
          <el-button type="primary" style="width: 80%;" @click="handleSave">Save</el-button>
        </div>
      </el-aside>
      <el-main>
        <!-- <tabs /> -->
        <!-- <inCoder :options="cmOptions" :value="code" /> -->
        <codemirror
          ref="codemirror"
          v-model="code"
          class="codemirror"
          :options="cmOptions"
          @ready="onCmReady"
          @focus="onCmFocus"
          @input="onCmCodeChange"
        />
      </el-main>
    </el-container>

    <el-dialog :title="dialogTitle" :visible.sync="dialogFormVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="dialogFormData" enctype="multipart/form-data" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;" @submit.native.prevent>
        <el-form-item label="Name" prop="name">
          <el-input v-model="dialogFormData.name" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">
          Cancel
        </el-button>
        <el-button type="primary" @click="handleDialogConfirm">
          Confirm
        </el-button>
      </div>
    </el-dialog>

    <el-dialog title="Warning" :visible.sync="deleteDialogVisible" width="30%">
      <span>Are you sure to delete?</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="deleteNode">Delete</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { codemirror } from 'vue-codemirror';
import { getTreePath, getFile, updateFile, renameFile, renameDirectory, createFile, createDirectory, deleteFile, deleteDirectory } from '@/api/tree';
// import tabs from './tabs';
import 'codemirror/lib/codemirror.css';

import 'codemirror/mode/javascript/javascript.js';
import 'codemirror/mode/css/css.js';
import 'codemirror/mode/xml/xml.js';
import 'codemirror/mode/clike/clike.js';
import 'codemirror/mode/markdown/markdown.js';
import 'codemirror/mode/python/python.js';
import 'codemirror/mode/r/r.js';
import 'codemirror/mode/shell/shell.js';
import 'codemirror/mode/sql/sql.js';
import 'codemirror/mode/swift/swift.js';
import 'codemirror/mode/vue/vue.js';

import 'codemirror/theme/cobalt.css';

// import 'codemirror/addon/fold/foldcode.js';
// import 'codemirror/addon/fold/foldgutter.js';
// import 'codemirror/addon/fold/brace-fold.js';
// import 'codemirror/addon/fold/xml-fold.js';
// import 'codemirror/addon/fold/indent-fold.js';
// import 'codemirror/addon/fold/markdown-fold.js';
// import 'codemirror/addon/fold/comment-fold.js';

export default {
    name: 'WebIDE',
    components: {
        // tabs: tabs,
        codemirror: codemirror
    },
    data() {
        const validateName = (rule, value, callback) => {
            if (value.length === 0) {
                return callback(new Error('Name is required'));
            }
            const invalidChars = '\\/:*?"<>|'.split('');
            for (const char of invalidChars) {
                if (value.includes(char)) {
                    return callback(new Error('Invalid input'));
                }
            }
            callback();
        };
        return {
            deleteDialogVisible: false,
            dialogRules: {
                name: [{
                    required: true,
                    validator: validateName,
                    trigger: 'change'
                }]
            },
            dialogFormData: {
                name: ''
            },
            dialogTitle: '',
            selectedNode: undefined,
            dialogFormVisible: false,
            contextMenuVisible: false,
            contextMenuTarget: undefined,
            currentFile: '',
            uuid: this.$route.query.uuid,
            props: {
                label: 'name',
                children: 'children',
                isLeaf: 'isLeaf'
            },
            code: '',
            cmOptions: {
                // codemirror options
                tabSize: 4,
                theme: 'cobalt',
                mode: 'text/x-c++src',
                lineNumbers: true
                // line: true
            }
        };
    },
    mounted() {
        this.$nextTick(() => {
            // vue-context-menu 需要传入一个触发右键事件的元素，等页面 dom 渲染完毕后才可获取
            this.contextMenuTarget = document.querySelector('#el-tree');
            // get all treeitem to listen to right click event
            const tree = document.querySelectorAll('#el-tree [role="treeitem"]');
            tree.forEach(item => {
                item.addEventListener('contextmenu', event => {
                    // if right click, then left click to get the current node.
                    event.target.click();
                });
            });
        });
    },
    methods: {
        onCmReady(cm) {
            console.log('the editor is readied!', cm);
        },
        onCmFocus(cm) {
            console.log('the editor is focus!', cm);
        },
        onCmCodeChange(newCode) {
            console.log('editor update');
        },
        getIconClass(filename) {
            if (filename.endsWith('/')) {
                return 'folder_closed';
            }
            const supportedSuffixes = ['c', 'cpp', 'cs', 'java', 'js', 'json', 'md', 'py', 's', 'txt'];
            const suffix = filename.substr(filename.lastIndexOf('.') + 1);
            const icon = (supportedSuffixes.includes(suffix) ? suffix : 'file');
            return icon;
        },
        handleRename() {
            // close context menu
            this.contextMenuVisible = false;
            // open rename window
            this.dialogTitle = 'Rename';
            this.dialogFormData.name = this.selectedNode.data.name;
            if (this.dialogFormData.name.endsWith('/')) {
                this.dialogFormData.name = this.dialogFormData.name.substr(0, this.dialogFormData.name.length - 1);
            }
            this.dialogFormVisible = true;
        },
        handleDelete() {
            this.contextMenuVisible = false;
            this.deleteDialogVisible = true;
        },
        deleteNode() {
            if (this.isDirectory(this.selectedNode.data.label)) {
                // delete dir
                deleteDirectory(this.uuid, this.selectedNode.data.label)
                    .then(response => {
                        this.$message({
                            message: 'Successfully Deleted',
                            type: 'success'
                        });
                        this.deleteDialogVisible = false;
                        // frontend delete
                        this.$refs.tree.remove(this.selectedNode);
                    });
            } else {
                // delete file
                deleteFile(this.uuid, this.selectedNode.data.label)
                    .then(response => {
                        this.$message({
                            message: 'Successfully Deleted',
                            type: 'success'
                        });
                        this.deleteDialogVisible = false;
                        // frontend delete
                        this.$refs.tree.remove(this.selectedNode);
                    });
            }
        },
        isDirectory(path) {
            return path.endsWith('/');
        },
        handleDialogConfirm() {
            this.$refs.dialogForm.validate(valid => {
                if (!valid) {
                    return false;
                }
                if (this.dialogTitle === 'Rename') {
                    // rename file or directory
                    if (this.isDirectory(this.selectedNode.data.label)) {
                        // rename dir
                        const oldPath = this.selectedNode.data.label;
                        const dir = oldPath.substr(0, oldPath.substr(0, oldPath.length - 1).lastIndexOf('/') + 1);
                        renameDirectory(this.uuid, this.selectedNode.data.label, dir + this.dialogFormData.name + '/')
                            .then(response => {
                                this.$message({
                                    message: 'Successfully Renamed',
                                    type: 'success'
                                });
                                this.dialogFormVisible = false;
                                // frontend rename
                                this.selectedNode.data.name = this.dialogFormData.name + '/';
                                this.selectedNode.data.label = dir + this.dialogFormData.name + '/';
                            });
                    } else {
                        const dir = this.selectedNode.data.label.substr(0, this.selectedNode.data.label.lastIndexOf('/') + 1);
                        renameFile(this.uuid, this.selectedNode.data.label, dir + this.dialogFormData.name)
                            .then(response => {
                                this.$message({
                                    message: 'Successfully Renamed',
                                    type: 'success'
                                });
                                this.dialogFormVisible = false;
                                // frontend rename
                                this.selectedNode.data.name = this.dialogFormData.name;
                                this.selectedNode.data.label = dir + this.dialogFormData.name;
                                this.selectedNode.data.icon = this.getIconClass(this.selectedNode.data.label);
                            });
                    }
                } else {
                    // create file or dir
                    if (!this.isDirectory(this.selectedNode.data.label)) {
                        this.selectedNode = this.selectedNode.parent;
                    }
                    if (this.dialogTitle === 'Create File') {
                        // create file
                        createFile(this.uuid, this.selectedNode.data.label + this.dialogFormData.name).then(response => {
                            this.$message({
                                message: 'Successfully Created',
                                type: 'success'
                            });
                            this.dialogFormVisible = false;
                            // frontend create
                            this.$refs.tree.append({
                                name: this.dialogFormData.name,
                                label: this.selectedNode.data.label + this.dialogFormData.name,
                                isLeaf: true,
                                icon: this.getIconClass(this.selectedNode.data.label + this.dialogFormData.name)
                            }, this.selectedNode);
                        });
                    } else {
                        // create directory
                        const newBasePath = this.dialogFormData.name + '/';
                        const newPath = this.selectedNode.data.label + newBasePath;
                        createDirectory(this.uuid, newPath).then(response => {
                            this.$message({
                                message: 'Successfully Created',
                                type: 'success'
                            });
                            this.dialogFormVisible = false;
                            // frontend create
                            this.$refs.tree.append({
                                name: newBasePath,
                                label: newPath,
                                isLeaf: false,
                                icon: this.getIconClass(newPath)
                            }, this.selectedNode);
                        });
                    }
                }
            });
        },
        loadNode(node, resolve) {
            if (node.level === 0) {
                resolve([{
                    label: '~/',
                    name: '~/',
                    isLeaf: false,
                    icon: 'folder_closed'
                }]);
                this.selectedNode = node.childNodes[0];
                return;
            }

            getTreePath(this.uuid, node.data.label).then(response => {
                const paths = response.payload;
                let resolveData = [];
                for (const path of paths) {
                    resolveData = resolveData.concat({
                        name: path,
                        label: node.data.label + path,
                        isLeaf: !this.isDirectory(path),
                        icon: this.getIconClass(path)
                    });
                }
                node.data.icon = 'folder_open';
                return resolve(resolveData);
            }).catch(() => {

            });
        },
        handleNodeClick(nodeObj, node, nodeComponent) {
            this.selectedNode = node;
            if (node.data.label.charAt(node.data.label.length - 1) === '/') {
                node.data.icon = (node.expanded ? 'folder_open' : 'folder_closed');
                return;
            }
            this.currentFile = node.data.label;
            getFile(this.uuid, this.currentFile).then(response => {
                this.code = response.payload;

                if (this.currentFile.endsWith('.cpp') || this.currentFile.endsWith('.c') || this.currentFile.endsWith('.s')) {
                    this.cmOptions.mode = 'text/x-c++src';
                } else if (this.currentFile.endsWith('.js')) {
                    this.cmOptions.mode = 'text/javascript';
                }
            });
        },
        handleCreateFile() {
            this.dialogTitle = 'Create File';
            this.dialogFormData.name = '';
            this.dialogFormVisible = true;
        },
        handleCreateDirectory() {
            this.dialogTitle = 'Create Directory';
            this.dialogFormData.name = '';
            this.dialogFormVisible = true;
        },
        handleSave() {
            updateFile(this.uuid, this.currentFile, this.code).then(response => {
                this.$message({
                    message: 'Code saved',
                    type: 'success'
                });
            });
        }
    }
};
</script>

<style lang="scss">
// .el-tree-node__expand-icon{
//     border:0;
//     background:url('../../icons/svg/box.svg');
//     content: '';
//     /*自定义，必要时用!important*/
// }
// .el-tree-node__expand-icon.expanded{
//     /*自定义，必要时用!important*/
// }
// .el-tree-node__expand-icon.is-leaf::before{
//     display: none;
// }

// .el-tree .el-tree-node__expand-icon.expanded
// {
//     -webkit-transform: rotate(0deg);
//     transform: rotate(0deg);
// }

.el-tree {
    height: 500px;
    .el-tree-node__content {
        height: 32px;
    }
    // .el-icon-caret-right:before
    // {
    //     background: url('https://dev.w3.org/SVG/tools/svgweb/samples/svg-files/410.svg') no-repeat 0 3px;
    //     content: '';
    //     // display: block;
    //     // width: 18px;
    //     // height: 18px;
    //     // font-size: 18px;
    //     // background-size: 18px;
    // }
    // .el-tree-node__expand-icon.expanded.el-icon-caret-right:before
    // {
    //     background: url('https://dev.w3.org/SVG/tools/svgweb/samples/svg-files/410.svg') no-repeat 0 3px;
    //     content: '';
    //     display: block;
    //     // width: 18px;
    //     // height: 18px;
    //     // font-size: 18px;
    //     // background-size: 18px;
    // }
}

.custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;
}

// .el-tree-node__expand-icon.is-leaf::before
// {
//     display: none;
// }

.codemirror{
    height: 80vh !important;
    .CodeMirror {
        font-family: Consolas, monaco, monospace;
        z-index: 1;
        height: 80vh !important;
        .CodeMirror-code {
            line-height: 19px;
        }
        .CodeMirror-scroll {
            overflow-y: hidden;
        }
    }
}

.right-menu {
    position: fixed;
    background: #ffffff;
    border: solid 1px #ffffff;
    border-radius: 5px;
    z-index: 999;
    display: none;
    box-shadow: 0 0.5em 1em 0 rgba(0,0,0,.1);
    a{
        padding: 8px;
        // line-height: 28px;
        font-size: 14px;
        text-align: center;
        display: block;
        color: #1a1a1a;
        text-decoration: none;
    }
    a:hover{
        color: #ffffff;
        background: #42b983;
        border: solid 1px #ffffff;
        border-radius: 5px;
    }
}

</style>
