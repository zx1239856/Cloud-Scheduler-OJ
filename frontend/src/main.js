// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import App from './App';
import router from './router';
import Config from './config';
import VueResource from 'vue-resource';
import Router from 'vue-router';
import ElementUI from 'element-ui';

import 'element-ui/lib/theme-chalk/index.css';
import 'xterm/css/xterm.css';
import './icons'; // icon

Vue.use(ElementUI);
Vue.use(Router);
Vue.use(VueResource);

Vue.config.productionTip = false;

Vue.http.options.root = (process.env.NODE_ENV === 'production' ? Config.prod.apiUrl : Config.dev.apiUrl);
Vue.http.options.ws_root = (process.env.NODE_ENV === 'production' ? Config.prod.wsUrl : Config.dev.wsUrl);

/* eslint-disable no-new */
new Vue({
    el: '#app',
    router,
    components: { App },
    template: '<App/>'
});
