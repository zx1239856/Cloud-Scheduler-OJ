<template>
  <div class="fullscreen">
    <div v-for="line in loglines" :key="line" class="item log-item" style="padding-top: 5px; padding-left: 5px;">
      <el-tag type="info" size="small" effect="dark">{{ uuid }}</el-tag>
      <span style="color: white;">{{ line }}</span>
    </div>
  </div>
</template>

<script>
import { getTask } from '@/api/task';

export default {
    data() {
        return {
            loglines: [],
            uuid: this.$route.query.uuid
        };
    },
    mounted() {
        getTask(this.$route.query.uuid).then(response => {
            this.loglines = response.payload.log.trim().split('\n');
        });
    },
    methods: {
    }
};
</script>

<style lang="scss" scoped>
.fullscreen {
    padding: 0px;
    min-height: 100vh;
    background-color: rgb(43, 41, 41);
}
</style>
