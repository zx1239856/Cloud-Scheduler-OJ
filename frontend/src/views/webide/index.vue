<template>
  <div class="container">
    <el-container @keyup.ctrl.83="handleSave">
      <el-aside width="300px">
        <el-tree
          :props="props"
          :load="loadNode"
          lazy
          @node-click="handleNodeClick"
        />
      </el-aside>
      <el-main>
        <!-- <tabs /> -->
        <!-- <inCoder :options="cmOptions" :value="code" /> -->
        <codemirror
          ref="codemirror"
          class="codemirror"
          :value="code"
          :options="cmOptions"
          @ready="onCmReady"
          @focus="onCmFocus"
          @input="onCmCodeChange"
        />
        <el-button type="primary" style="margin-top: 10px;" @click="handleSave">Save</el-button>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
.container {
  min-height: inherit;
  min-width: 100%;
}
</style>

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
            currentFile: '',
            uuid: this.$route.query.uuid,
            props: {
                label: 'name',
                children: 'zones',
                isLeaf: 'leaf'
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
    },
    methods: {
        onCmReady(cm) {
            console.log('the editor is readied!', cm);
        },
        onCmFocus(cm) {
            console.log('the editor is focus!', cm);
        },
        onCmCodeChange(newCode) {
            console.log('update');
            // this.code = newCode;
        },
        loadNode(node, resolve) {
            if (node.level === 0) {
                return resolve([{
                    label: '~/',
                    name: '~/',
                    leaf: false
                }]);
            }
            getTreePath(this.uuid, node.data.label).then(response => {
                const paths = response.payload;
                let resolveData = [];
                for (const path of paths) {
                    const isLeaf = (path.charAt(path.length - 1) !== '/');
                    resolveData = resolveData.concat({
                        name: path,
                        label: node.data.label + path,
                        leaf: isLeaf
                    });
                }
                return resolve(resolveData);
            }).catch(() => {
                resolve([]);
            });
        },
        handleNodeClick(nodeObj, node, nodeComponent) {
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
            console.log('save');
        }
    }
};
</script>

<style lang="scss">

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

.code-mode-select {
    position: absolute;
    z-index: 2;
    right: 25px;
    top: 10px;
    max-width: 130px;
}

</style>
