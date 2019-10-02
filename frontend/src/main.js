// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import App from './App';
import router from './router';
import Config from './config';

Vue.config.productionTip = false;

Vue.http.options.root = (process.env.NODE_ENV === 'production' ? Config.prod.apiUrl : Config.dev.apiUrl);

/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    components: { App },
    template: '<App/>'
});
