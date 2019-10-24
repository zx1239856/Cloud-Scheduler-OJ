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
    >
      <el-table-column label="Repository" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.Repo }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Number of Tags" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.NumberOfTags }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Size" min-width="200" align="center">
        <template slot-scope="scope">
          <span>{{ scope.row.SizeOfRepository }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" width="150" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <el-row>
            <el-button type="primary" size="mini" @click="handleImageInfo(row)">
              Images
            </el-button>
          </el-row>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" :page-sizes="pageSizes" @pagination="getRepositories" />
  </div>
</template>

<script>
import { getRepositories } from '@/api/registry';
import waves from '@/directive/waves'; // waves directive
import Pagination from '@/components/Pagination'; // secondary package based on el-pagination

export default {
    name: 'RepositoryList',
    components: { Pagination },
    directives: { waves },
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
            }
        };
    },
    created() {
        this.getRepositoryList();
    },
    methods: {
        getRepositoryList() {
            this.listLoading = true;
            getRepositories(this.listQuery).then(response => {
                this.list = response.payload.entity;
                this.total = response.payload.count;
                this.listLoading = false;
            });
        },
        handleImageInfo(row) {
            const routeData = this.$router.resolve({ name: 'image', query: { repo: row.Repo }});
            window.open(routeData.href);
        }
    }
};
</script>
