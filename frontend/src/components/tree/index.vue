<template>
  <div class="app-container">
    <el-input v-model="filterText" placeholder="Filter keyword" style="margin-bottom:30px;" />
    <el-dropdown>
      <span class="el-dropdown-link">
        Operations<i class="el-icon-arrow-down el-icon--right" />
      </span>
      <el-dropdown-menu slot="dropdown">
        <el-dropdown-item>add file</el-dropdown-item>
        <el-dropdown-item divided>add directory</el-dropdown-item>
      </el-dropdown-menu>
    </el-dropdown>
    <el-tree
      ref="tree2"
      :data="data"
      :filter-node-method="filterNode"
      :props="defaultProps"
      class="filter-tree"
      @node-click="handleNodeClick"
    />
  </div>
</template>

<style>
  .el-dropdown-link {
    cursor: pointer;
    color: #409EFF;
  }
  .el-icon-arrow-down {
    font-size: 12px;
  }
</style>

<script>
import { getTree } from '@/api/tree';

export default {
    name: 'Tree',
    props: {
        tree: {
            type: Object,
            default: () => {}
        }
    },
    data() {
        return {
            filterText: '',
            listQuery: {
                pod: this.tree.podName,
                namespace: this.tree.namespace
            },
            basepath: this.tree.podName + '/' + this.tree.namespaces + '/',
            data: [{
                label: '一级 1',
                children: [{
                    label: '二级 1-1',
                    children: [{
                        label: '三级 1-1-1'
                    }]
                }]
            }],
            // data2: null,
            defaultProps: {
                children: 'children',
                label: 'label'
            }
        };
    },
    watch: {
        filterText(val) {
            this.$refs.tree2.filter(val);
        }
    },
    created() {
        this.data = getTree(this.listQuery);
    },
    mounted() {
        console.log('pid: ' + this.tree.pid + ' is on ready');
        this.data = getTree(this.listQuery);
    },
    methods: {
        filterNode(value, data) {
            if (!value) return true;
            return data.label.indexOf(value) !== -1;
        },
        handleNodeClick(data) {
            console.log(data);
        }
    }
};
</script>

