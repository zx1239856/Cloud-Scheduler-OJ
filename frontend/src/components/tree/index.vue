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
                namespace: this.tree.namespace,
                path: this.path
            },
            pathToId: {},
            data: [],
            defaultProps: {
                children: 'children',
                label: 'label',
                path: ''
            }
        };
    },
    watch: {
        filterText(val) {
            this.$refs.tree2.filter(val);
        }
    },
    created() {
        this.getCurrentTree('.');
    },
    methods: {
        getCurrentTree(path, nodeId) {
            console.log(path);
            console.log(nodeId);
            this.listQuery.path = path;
            console.log(this.listQuery);
            getTree(this.listQuery).then(response => {
                const resp_data = response.payload;
                const data = [];
                for (let i = 0; i < resp_data.directories.length; i++) {
                    let name = resp_data.directories[i];
                    if (name != null && name.length > 0 && name.charAt(name.length - 1) === '/') {
                        name = name.substring(0, name.length - 1);
                    }
                    data.push({ label: name, children: [{}], path: path });
                }
                for (let i = 0; i < resp_data.files.length; i++) {
                    let name = resp_data.files[i];
                    if (name != null && name.length > 0 && name.charAt(name.length - 1) === '/') {
                        name = name.substring(0, name.length - 1);
                    }
                    data.push({ label: name, path: path });
                }
                console.log(data);
                const pathList = path.split('/');
                if (data.length !== 0) {
                    this.data = this.addData(this.data, data, pathList, 0, nodeId);
                }
            });
        },
        addData(currentDirectory, data, pathList, index, nodeId) {
            console.log(index);
            if (index === pathList.length - 1) {
                return data;
            }
            // if (index === 0) {
            //     if (currentDirectory.length === 0) {
            //         return data;
            //     }
            //     index++;
            //     for (let i = 0; i < currentDirectory.length; i++) {
            //         if (currentDirectory[i].label === pathList[index]) {
            //             currentDirectory[i].children = this.addData(currentDirectory[i].children, data, pathList, index, nodeId);
            //             return currentDirectory;
            //         }
            //     }
            // }
            // console.log('here');
            if (currentDirectory.length === 0) {
                return data;
            }
            index++;
            for (let i = 0; i < currentDirectory.length; i++) {
                console.log(currentDirectory[i]);
                if (currentDirectory[i].label === pathList[index] && 'children' in currentDirectory[i]) {
                    currentDirectory[i].children = this.addData(currentDirectory[i].children, data, pathList, index, nodeId);
                    return currentDirectory;
                }
            }
        },
        filterNode(value, data) {
            if (!value) return true;
            return data.label.indexOf(value) !== -1;
        },
        handleNodeClick(data) {
            console.log(data.label);
            console.log(data);
            console.log('children' in data);
            if ('children' in data && data.children.length === 1) {
                this.getCurrentTree(data.path + '/' + data.label, data.$treeNodeId);
            }
        }
    }
};
</script>

