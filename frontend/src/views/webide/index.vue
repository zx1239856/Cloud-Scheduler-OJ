<template>
  <div class="container">
    <el-container @keyup.ctrl.83="handleSave">
      <el-aside width="300px">
        <div style="margin: 20px;">
          <span>
            Edit
          </span>
          <span style="float: right;">
            <el-tooltip class="item" effect="dark" content="New File" placement="top">
              <svg-icon icon-class="new_file" style="cursor:pointer; margin-left: 5px;" />
            </el-tooltip>
            <el-tooltip class="item" effect="dark" content="New Directory" placement="top">
              <svg-icon icon-class="new_directory" style="cursor:pointer; margin-left: 5px;" />
            </el-tooltip>
          </span>
        </div>
        <hr style="margin: 0px; border-top: 0.5px solid #dcdfe6;">
        <div style="overflow-y: scroll;">
          <el-tree id="el-tree" :props="props" :load="loadNode" lazy highlight-current @node-click="handleNodeClick">
            <span slot-scope="{ node }" class="custom-tree-node">
              <span>
                <span>
                  <svg-icon v-if="!node.data.leaf && !node.data.expanded" icon-class="folder_closed" />
                  <svg-icon v-else-if="!node.data.leaf && node.data.expanded" icon-class="folder_open" />
                  <svg-icon v-else :icon-class="node.data.icon" />
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
            <a href="javascript:;" style="display: flex;" @click="renameNode">
              <svg-icon icon-class="rename" />
              <span style="float: right; margin-left: 5px;">Rename</span>
            </a>
            <a href="javascript:;" style="display: flex;" @click="deleteNode">
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
  </div>
</template>

<script>
import { codemirror } from 'vue-codemirror';
import { getTreePath, getFile, updateFile } from '@/api/tree';
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
        return {
            nodeData: {},
            contextMenuVisible: false,
            contextMenuTarget: undefined,
            currentFile: '',
            uuid: this.$route.query.uuid,
            props: {
                label: 'name',
                children: 'zones',
                isLeaf: 'leaf',
                icon: 'user'
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
            // 获取所有的 treeitem，循环监听右键事件
            const tree = document.querySelectorAll('#el-tree [role="treeitem"]');
            tree.forEach(item => {
                item.addEventListener('contextmenu', event => {
                    // 如果右键了，则模拟点击这个treeitem
                    // event.target.click();
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
        renameNode() {

        },
        deleteNode() {

        },
        loadNode(node, resolve) {
            if (node.level === 0) {
                return resolve([{
                    label: '~/',
                    name: '~/',
                    leaf: false,
                    icon: 'user'
                }]);
            }
            getTreePath(this.uuid, node.data.label).then(response => {
                const paths = response.payload;
                let resolveData = [];
                const supportedSuffixes = ['c', 'cpp', 'cs', 'java', 'js', 'json', 'md', 'py', 's', 'txt'];
                for (const path of paths) {
                    const isLeaf = (path.charAt(path.length - 1) !== '/');
                    const suffix = path.substr(path.lastIndexOf('.') + 1);

                    let icon = 'file';
                    if (supportedSuffixes.includes(suffix)) {
                        icon = suffix;
                    }
                    resolveData = resolveData.concat({
                        name: path,
                        label: node.data.label + path,
                        leaf: isLeaf,
                        icon: icon
                    });
                }
                return resolve(resolveData);
            }).catch(() => {
                resolve([]);
            });
        },
        handleNodeClick(nodeObj, node, nodeComponent) {
            this.nodeData = node.data;
            if (node.data.label.charAt(node.data.label.length - 1) === '/') {
                return;
            }
            this.currentFile = node.data.label;
            getFile(this.uuid, this.currentFile).then(response => {
                this.code = response.payload;

                if (this.currentFile.endsWith('.cpp') || this.currentFile.endsWith('.c') || this.currentFile.endsWith('.s')) {
                    this.cmOptions.mode = 'text/x-c++src';
                } else if (this.currentFile.endsWith('.js')) {
                    console.log('js');
                    this.cmOptions.mode = 'text/javascript';
                }
            });
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
