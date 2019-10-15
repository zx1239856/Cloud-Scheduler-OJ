<template>
  <div class="container">
    <!--div>
      <el-button plain @click="showDirDialog">打开</el-button>
    </div-->
    <el-container>
      <el-container>
        <!--左侧侧边栏-->
        <!--el-aside width="300px">
          <el-tree
            ref="dirTree"
            :data="dirTree"
            :load="loadSubFile"
            :props="defaultProps"
            lazy
            @node-click="treeNodeClick"
          />
        </el-aside-->
        <!--主-->
        <el-main>
          <!--编辑器-->
          <inCoder :options="cmOptions" :value="code" />
        </el-main>
      </el-container>
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
// import { codemirror } from 'vue-codemirror';
import inCoder from './Codemirror';
import 'codemirror/mode/python/python.js';
import 'codemirror/addon/fold/foldcode.js';
import 'codemirror/addon/fold/foldgutter.js';
import 'codemirror/addon/fold/brace-fold.js';
import 'codemirror/addon/fold/xml-fold.js';
import 'codemirror/addon/fold/indent-fold.js';
import 'codemirror/addon/fold/markdown-fold.js';
import 'codemirror/addon/fold/comment-fold.js';

export default {
    name: 'WebIDE',
    components: {
        inCoder
    },
    data() {
        return {
            code: '',
            cmOptions: {
                tabSize: 4,
                mode: 'text/javascript',
                lineNumbers: true
            }
        };
    },
    mounted() {},
    methods: {
        displayFileData(content) {
            this.code = content;
        }
    }
};
</script>
