import Vue from 'vue';
import Router from 'vue-router';
import VueResource from 'vue-resource';
import HelloWorld from '@/components/HelloWorld';
import WebSSH from '@/components/WebSSH';
import 'xterm/css/xterm.css';

Vue.use(Router);
Vue.use(VueResource);

export default new Router({
    mode: 'history',
    routes: [
        {
            path: '/',
            name: 'HelloWorld',
            component: HelloWorld
        },
        {
            path: '/WebSSH',
            name: 'WebSSH',
            component: WebSSH
        }
    ]
});
