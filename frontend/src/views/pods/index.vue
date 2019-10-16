<template>
  <div class="app-container">
    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      @sort-change="sortChange"
    >
      <el-table-column label="Namespace" width="150" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.namespace }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Name" min-width="150" align="center">
        <template slot-scope="{row}">
          <span>{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="IP" prop="ip" align="center" width="150">
        <template slot-scope="scope">
          <span>{{ scope.row.pod_ip }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Created Time" width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.create_time }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Status" class-name="status-col" width="150" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" width="150" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleTerminal(row)">
            Terminal
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getList" />
  </div>
</template>

<script>
import { getPodList } from '@/api/pods';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'PodList',
    components: { Pagination },
    directives: { waves },
    filters: {
        statusFilter(status) {
            const statusMap = {
                Succeeded: 'success',
                Failed: 'danger'
                // Running: 'info',
            };
            return statusMap[status];
        }
    },
    data() {
        return {
            tableKey: 0,
            list: null,
            total: 0,
            listLoading: true,
            pageSizes: [25],
            listQuery: {
                page: 1,
                limit: 25
            },
            rules: {
                type: [{ required: true, message: 'type is required', trigger: 'change' }],
                timestamp: [{ type: 'date', required: true, message: 'timestamp is required', trigger: 'change' }],
                title: [{ required: true, message: 'title is required', trigger: 'blur' }]
            }
        };
    },
    created() {
        this.getList();
    },
    methods: {
        getList() {
            this.listLoading = true;

            getPodList(this.listQuery).then(response => {
                this.list = response.payload.entry;
                this.total = response.payload.count;

                // Just to simulate the time of the request
                setTimeout(() => {
                    this.listLoading = false;
                }, 0.5 * 1000);
            });
        },
        handleTerminal(row) {
            const routeData = this.$router.resolve({ name: 'webssh', query: { pod: row.name, namespace: row.namespace }});
            window.open(routeData.href, '_blank');
        },
        sortChange(data) {
            const { prop, order } = data;
            console.log(prop);
            console.log(order);
        },
        resetTemp() {
            this.temp = {
                id: undefined,
                importance: 1,
                remark: '',
                timestamp: new Date(),
                title: '',
                status: 'published',
                type: ''
            };
        }
    }
};
</script>
