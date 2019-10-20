<template>
  <div class="container">
    <el-container>
      <el-aside width="300px">
        <tree />
      </el-aside>
      <el-main>
        <tabs />
        <inCoder :options="cmOptions" :value="code" />
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
import inCoder from './Codemirror';
import tree from '../tree/index';
import tabs from './tabs';
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
        inCoder,
        tree,
        tabs
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
