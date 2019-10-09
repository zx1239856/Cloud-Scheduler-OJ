import Router from 'vue-router';
import HelloWorld from '@/components/HelloWorld';
import Login from '@/components/Login';
import WebSSH from '@/components/WebSSH';

export default new Router({
    mode: 'history',
    routes: [
        {
            path: '/',
            name: 'HelloWorld',
            redirect: '/login',
            component: HelloWorld
        },
        {
            path: '/login',
            name: 'Login',
            component: Login
        },
        {
            path: '/web-ssh',
            name: 'WebSSH',
            component: WebSSH
        }
    ]
});
