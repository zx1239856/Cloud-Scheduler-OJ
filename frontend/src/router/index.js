import Router from 'vue-router';
import HelloWorld from '@/components/HelloWorld';
import Login from '@/components/Login';
import WebSSH from '@/components/WebSSH';
import WebIDE from '@/components/WebIDE';

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
        },
        {
            path: '/web-ide',
            name: 'WebIDE',
            component: WebIDE
        }
    ]
});
