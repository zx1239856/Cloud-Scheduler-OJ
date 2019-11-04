<template>
  <div class="container">
    <el-container>
      <el-aside width="300px">
        <div style="height: 50px; padding: 18px;">
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
          <v-contextmenu ref="contextmenu">
            <v-contextmenu-item @click="handleRename">
              <svg-icon icon-class="rename" />
              <span style="margin-left: 5px;">Rename</span>
            </v-contextmenu-item>
            <v-contextmenu-item @click="handleDelete">
              <svg-icon icon-class="delete" />
              <span style="margin-left: 5px;">Delete</span>
            </v-contextmenu-item>
          </v-contextmenu>

          <el-tree id="el-tree" ref="tree" node-key="key" :props="props" :load="loadNode" lazy highlight-current @node-click="handleNodeClick" @node-contextmenu="handleNodeContextMenu" @click.native.prevent="handleNodeClick">
            <span slot-scope="{ node }" class="custom-tree-node">
              <span>
                <span>
                  <svg-icon :icon-class="node.data.icon" />
                </span>
                <span style="margin-left: 5px;">{{ node.data.label }}</span>
              </span>
            </span>
          </el-tree>
        </div>
        <hr style="margin: 0px; border-top: 0.5px solid #dcdfe6;">
        <div style="text-align: center; margin: 20px;">
          <el-button type="primary" style="width: 80%;" @click="handleSave">Save</el-button>
        </div>
      </el-aside>
      <el-divider direction="vertical" />
      <el-main v-loading="codeMirrorLoading" style="padding: 0px;">
        <div style="height: 50px; padding-top: 9px;">
          <el-tabs v-if="tabs.length" v-model="currentFile" type="border-card" closable @edit="handleTabsEdit" @tab-click="handleTabClick">
            <el-tab-pane v-for="item in tabs" :key="item.key" :label="item.label" :name="item.key" tab-position="bottom" />
          </el-tabs>
        </div>
        <div @keydown.ctrl.83.prevent="handleSave">
          <codemirror
            v-if="tabs.length"
            ref="codemirror"
            v-model="code"
            class="codemirror"
            :options="cmOptions"
            @ready="onCmReady"
            @focus="onCmFocus"
            @input="onCmCodeChange"
          />
        </div>
      </el-main>
    </el-container>

    <el-dialog :title="dialogTitle" :visible.sync="dialogFormVisible">
      <el-form ref="dialogForm" :rules="dialogRules" :model="dialogFormData" enctype="multipart/form-data" label-position="left" label-width="110px" style="width: 480px; margin-left:50px;" @submit.native.prevent>
        <el-form-item label="Name" prop="name">
          <el-input ref="inputName" v-model="dialogFormData.name" @keyup.enter.native="handleDialogConfirm" />
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
      <span>Are you sure to delete {{ selectedNode ? selectedNode.data.key : '' }}?</span>
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
import 'codemirror/mode/gas/gas.js';
import 'codemirror/mode/htmlembedded/htmlembedded.js';

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
            tabs: [],
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
            topLevelNode: undefined,
            dialogFormVisible: false,
            contextMenuVisible: false,
            contextMenuTarget: undefined,
            currentFile: '',
            uuid: this.$route.query.uuid,
            props: {
                label: 'label',
                key: 'key',
                children: 'children',
                isLeaf: 'isLeaf'
            },
            codeMirrorLoading: false,
            code: '',
            cmOptions: {
                // codemirror options
                tabSize: 2,
                mode: 'javascript',
                lineNumbers: true
                // line: true
            },
            modeMap: {
                js: 'javascript',
                css: 'css',
                xml: 'xml',
                cpp: 'text/x-c++src',
                c: 'text/x-csrc',
                java: 'text/x-java',
                cs: 'text/x-csharp',
                m: 'text/x-objectivec',
                scala: 'text/x-scala',
                md: 'markdown',
                py: 'python',
                r: 'r',
                sh: 'shell',
                sql: 'sql',
                swift: 'swift',
                vue: 'vue',
                txt: '',
                s: { name: 'gas', architecture: 'x86' },
                html: 'application/x-ejs'
            }
        };
    },
    methods: {
        onCmReady(cm) {

        },
        onCmFocus(cm) {

        },
        onCmCodeChange(newCode) {
            const tabIndex = this.getTabIndexOfFile(this.currentFile);
            if (tabIndex > -1) {
                this.tabs[tabIndex].content = this.code;
            }
        },
        getHighlightMode(filename) {
            if (!filename) {
                return '';
            }

            for (const extension in this.modeMap) {
                if (this.currentFile.endsWith('.' + extension)) {
                    return this.modeMap[extension];
                }
            }
            return '';
        },
        handleTabsEdit(targetKey, action) {
            if (action === 'remove') {
                if (this.currentFile === targetKey) {
                    this.tabs.forEach((tabs, index) => {
                        if (tabs.key === targetKey) {
                            const nextTab = this.tabs[index + 1] || this.tabs[index - 1];
                            if (nextTab) {
                                this.currentFile = nextTab.key;
                                this.code = nextTab.content;
                                this.cmOptions.mode = this.getHighlightMode(this.currentFile);
                            }
                        }
                    });
                }
                this.tabs = this.tabs.filter(tab => tab.key !== targetKey);
            }
        },
        getIconClass(filename) {
            if (filename.endsWith('/')) {
                return 'folder_closed';
            }
            for (const extension in this.modeMap) {
                if (filename.endsWith('.' + extension)) {
                    return extension;
                }
            }
            return 'file';
        },
        handleRename() {
            // close context menu
            this.contextMenuVisible = false;
            // open rename window
            this.dialogTitle = 'Rename';
            this.dialogFormData.name = this.selectedNode.data.label;
            if (this.dialogFormData.name.endsWith('/')) {
                this.dialogFormData.name = this.dialogFormData.name.substr(0, this.dialogFormData.name.length - 1);
            }
            this.dialogFormVisible = true;
            this.$nextTick(() => {
                this.$refs.inputName.focus();
            });
        },
        handleDelete() {
            this.contextMenuVisible = false;
            this.deleteDialogVisible = true;
        },
        deleteNode() {
            if (this.isDirectory(this.selectedNode.data.key)) {
                // delete dir
                deleteDirectory(this.uuid, this.selectedNode.data.key)
                    .then(response => {
                        this.$message({
                            message: 'Successfully Deleted',
                            type: 'success'
                        });
                        this.deleteDialogVisible = false;
                        // frontend delete
                        this.$refs.tree.remove(this.selectedNode);
                        this.selectedNode = this.topLevelNode;
                    });
            } else {
                // delete file
                deleteFile(this.uuid, this.selectedNode.data.key)
                    .then(response => {
                        this.$message({
                            message: 'Successfully Deleted',
                            type: 'success'
                        });
                        this.deleteDialogVisible = false;
                        // frontend delete
                        this.$refs.tree.remove(this.selectedNode);
                        this.selectedNode = this.topLevelNode;
                    });
            }
        },
        handleTabClick(tab) {
            if (this.codeMirrorLoading) {
                this.$message('Loading. Please wait!');
                return;
            }
            this.currentFile = this.tabs[tab.index].key;
            this.code = this.tabs[tab.index].content;
            this.cmOptions.mode = this.getHighlightMode(this.currentFile);
        },
        getTabIndexOfFile(path) {
            let tabIndex = -1;
            this.tabs.forEach((tab, index) => {
                if (tab.key === path) {
                    tabIndex = index;
                }
            });
            return tabIndex;
        },
        isDirectory(path) {
            return path.endsWith('/');
        },
        handleDialogConfirm() {
            this.$refs.dialogForm.validate(valid => {
                if (!valid) {
                    return false;
                }
                if (!this.selectedNode) {
                    this.selectedNode = this.topLevelNode;
                }
                if (this.dialogTitle === 'Rename') {
                    // rename file or directory
                    if (this.isDirectory(this.selectedNode.data.key)) {
                        // rename dir
                        const oldPath = this.selectedNode.data.key;
                        const dir = oldPath.substr(0, oldPath.substr(0, oldPath.length - 1).lastIndexOf('/') + 1);
                        renameDirectory(this.uuid, this.selectedNode.data.key, dir + this.dialogFormData.name + '/')
                            .then(response => {
                                this.$message({
                                    message: 'Successfully Renamed',
                                    type: 'success'
                                });
                                this.dialogFormVisible = false;
                                // frontend rename
                                this.selectedNode.data.label = this.dialogFormData.name + '/';
                                this.selectedNode.data.key = dir + this.dialogFormData.name + '/';
                            });
                    } else {
                        const dir = this.selectedNode.data.key.substr(0, this.selectedNode.data.key.lastIndexOf('/') + 1);
                        renameFile(this.uuid, this.selectedNode.data.key, dir + this.dialogFormData.name)
                            .then(response => {
                                this.$message({
                                    message: 'Successfully Renamed',
                                    type: 'success'
                                });
                                this.dialogFormVisible = false;
                                // frontend rename
                                this.selectedNode.data.label = this.dialogFormData.name;
                                this.selectedNode.data.key = dir + this.dialogFormData.name;
                                this.selectedNode.data.icon = this.getIconClass(this.selectedNode.data.key);
                            });
                    }
                } else {
                    // create file or dir
                    if (!this.isDirectory(this.selectedNode.data.key)) {
                        this.selectedNode = this.selectedNode.parent;
                    }
                    if (this.dialogTitle === 'Create File') {
                        // create file
                        createFile(this.uuid, this.selectedNode.data.key + this.dialogFormData.name).then(response => {
                            this.$message({
                                message: 'Successfully Created',
                                type: 'success'
                            });
                            this.dialogFormVisible = false;
                            // frontend create
                            this.$refs.tree.append({
                                label: this.dialogFormData.name,
                                key: this.selectedNode.data.key + this.dialogFormData.name,
                                isLeaf: true,
                                icon: this.getIconClass(this.selectedNode.data.key + this.dialogFormData.name)
                            }, this.selectedNode);
                        });
                    } else {
                        // create directory
                        const newBasePath = this.dialogFormData.name + '/';
                        const newPath = this.selectedNode.data.key + newBasePath;
                        createDirectory(this.uuid, newPath).then(response => {
                            this.$message({
                                message: 'Successfully Created',
                                type: 'success'
                            });
                            this.dialogFormVisible = false;
                            // frontend create
                            this.$refs.tree.append({
                                label: newBasePath,
                                key: newPath,
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
                    key: '~/',
                    label: '~/',
                    isLeaf: false,
                    icon: 'folder_closed'
                }]);
                this.topLevelNode = node.childNodes[0];
                return;
            }

            getTreePath(this.uuid, node.data.key).then(response => {
                const paths = response.payload;
                let resolveData = [];
                for (const path of paths) {
                    resolveData = resolveData.concat({
                        label: path,
                        key: node.data.key + path,
                        isLeaf: !this.isDirectory(path),
                        icon: this.getIconClass(path)
                    });
                }
                node.data.icon = 'folder_open';
                return resolve(resolveData);
            }).catch(() => {

            });
        },
        handleNodeContextMenu(event, nodeObj, node, nodeComponent) {
            this.selectedNode = node;
            this.$refs.contextmenu.show({ top: event.pageY, left: event.pageX });
        },
        handleNodeClick(nodeObj, node, nodeComponent) {
            if (this.codeMirrorLoading) {
                this.$message('Loading. Please wait!');
                return;
            }
            if (!node) {
                this.selectedNode = this.topLevelNode;
                this.$refs.tree.setCurrentNode(this.topLevelNode);
                return;
            }
            this.selectedNode = node;
            if (node.data.key.charAt(node.data.key.length - 1) === '/') {
                node.data.icon = (node.expanded ? 'folder_open' : 'folder_closed');
                return;
            }

            const tabIndex = this.getTabIndexOfFile(node.data.key);
            if (tabIndex > -1) {
                this.currentFile = this.tabs[tabIndex].key;
                this.code = this.tabs[tabIndex].content;
                this.cmOptions.mode = this.getHighlightMode(this.currentFile);
                return;
            }

            this.codeMirrorLoading = true;
            this.currentFile = node.data.key;

            getFile(this.uuid, this.currentFile).then(response => {
                this.code = response.payload;
                this.cmOptions.mode = this.getHighlightMode(this.currentFile);
                this.tabs.push({
                    key: this.currentFile,
                    label: this.currentFile.substr(this.currentFile.lastIndexOf('/') + 1),
                    content: response.payload
                });
                this.codeMirrorLoading = false;
            });
        },
        handleCreateFile() {
            this.dialogTitle = 'Create File';
            this.dialogFormData.name = '';
            this.dialogFormVisible = true;
            this.$nextTick(() => {
                this.$refs.inputName.focus();
            });
        },
        handleCreateDirectory() {
            this.dialogTitle = 'Create Directory';
            this.dialogFormData.name = '';
            this.dialogFormVisible = true;
            this.$nextTick(() => {
                this.$refs.inputName.focus();
            });
        },
        handleSave() {
            this.codeMirrorLoading = true;
            updateFile(this.uuid, this.currentFile, this.code).then(response => {
                this.$message({
                    message: 'Code saved',
                    type: 'success'
                });
            }).finally(() => {
                this.codeMirrorLoading = false;
            });
        }
    }
};
</script>

<style lang="scss">
.el-tabs{
    .el-tabs__header{
        margin: 0px;
    }
    .el-tabs__content{
        margin: 0px;
    }
}

.el-tree {
    height: 75vh;
    .el-tree-node__content {
        height: 32px;
    }
}

.custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;
}

.vue-codemirror{
    height: 86vh;
    width: 100%;
    .CodeMirror {
        font-family: Consolas, monaco, monospace;
        z-index: 1;
        height: 100%;
        .CodeMirror-code {
            line-height: 19px;
        }
        .CodeMirror-scroll {
            overflow-y: scroll;
            overflow-x: scroll;
            padding: 0px;
        }
    }
}

.el-divider.el-divider--vertical {
    height: unset;
    margin: 0px;
}

.v-contextmenu-item{
    padding: 10px 16px 10px 16px !important;
}
</style>
