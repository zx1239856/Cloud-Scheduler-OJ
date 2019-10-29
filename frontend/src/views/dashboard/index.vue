<template>
  <div class="dashboard-container">
    <div class="dashboard-avatar">
      <el-avatar :size="150" :src="avatar" />
    </div>
    <div class="dashboard-text">Hello, {{ name }} !</div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'Dashboard',
    computed: {
        ...mapGetters([
            'name',
            'avatar'
        ])
    }
};
</script>

<style lang="scss" scoped>
.dashboard {
    &-container {
        margin: 30px;
    }
    &-text {
        margin-top: 5vh;
        font-size: 30px;
        line-height: 46px;
        text-align: center;
    }
    &-avatar {
        margin-top: 20vh;
        text-align: center;
    }
}
</style>
