import Router from 'vue-router';
import HelloWorld from '@/components/HelloWorld';
import WebSSH from '@/components/WebSSH';
import 'xterm/css/xterm.css';

Vue.use(Router);
Vue.use(VueResource);
import Login from '@/components/Login';

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
        },
        {
            path: '/login',
            name: 'Login',
            component: Login
        }
    ]
});
