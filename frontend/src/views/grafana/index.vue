<template>
  <div class="grafana-container">
    <div class="grafana-text">Grafana redirection</div>
  </div>
</template>

<script>
import Cookies from 'js-cookie';
import store from '@/store';

export default {
    name: 'Grafana',
    created() {
        const expire_time = new Date(new Date().getTime() + 2 * 60 * 1000); // two minutes
        Cookies.set('username', store.getters.name, { expires: expire_time });
        Cookies.set('token', store.getters.token, { expires: expire_time });
        const href = 'https://grafana.app.dropthu.online:30443/';
        window.open(href, '_blank');
    }
};
</script>

<style lang="scss" scoped>
.grafana {
    &-container {
        margin: 30px;
    }
    &-text {
        margin-top: 5vh;
        font-size: 30px;
        line-height: 46px;
        text-align: center;
    }
}
</style>
