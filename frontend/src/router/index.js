import Vue from 'vue';
import Router from 'vue-router';

Vue.use(Router);

/* Layout */
import Layout from '@/layout';

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'             the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
    {
        path: '/login',
        component: () => import('@/views/login/index'),
        hidden: true
    },
    {
        path: '/signup',
        component: () => import('@/views/signup/index'),
        hidden: true
    },
    {
        path: '/404',
        component: () => import('@/views/404'),
        hidden: true
    },
    {
        path: '/',
        component: Layout,
        redirect: '/dashboard',
        children: [{
            path: 'dashboard',
            name: 'Dashboard',
            component: () => import('@/views/dashboard/index'),
            meta: { title: 'Dashboard', icon: 'dashboard' }
        }]
    },
    {
        path: '/profile/',
        component: Layout,
        hidden: true,
        children: [{
            path: '/',
            name: 'profile',
            component: () => import('@/views/profile/index'),
            meta: { title: 'Dashboard' }
        }]
    },
    {
        path: '/task',
        name: 'task',
        component: Layout,
        meta: { title: 'Task', icon: 'task' },
        children: [
            {
                path: 'task-settings',
                name: 'task-settings',
                component: () => import('@/views/task_settings/index'),
                meta: { title: 'Task Settings' }
            },
            {
                path: 'task-settings-detail/',
                name: 'task-settings-detail',
                component: () => import('@/views/task_settings/detail'),
                meta: { title: 'Task Settings Detail', noCache: true, activeMenu: '/task/task-settings/' },
                hidden: true
            },
            {
                path: 'task-list',
                name: 'task-list',
                component: () => import('@/views/task/index'),
                meta: { title: 'Task List' }
            },
            {
                path: 'webide/',
                name: 'webide',
                hidden: true,
                component: () => import('@/views/webide/index'),
                meta: { title: 'Web IDE' }
            },
            {
                path: 'vnc-view/',
                name: 'vnc',
                hidden: true,
                component: () => import('@/views/vnc/index'),
                meta: { title: 'VNC Viewer' }
            }
        ]
    },
    {
        path: '/log/',
        name: 'log',
        component: () => import('@/views/log/index')
    },
    {
        path: '/webssh/',
        name: 'webssh',
        component: () => import('@/views/webssh/index')
    },
    {
        path: '/user-terminal/',
        name: 'user-terminal',
        component: () => import('@/views/user_terminal/index')
    },
    // 404 page must be placed at the end !!!
    { path: '*', redirect: '/404', hidden: true }
];

export const asyncRoutes = [
    {
        path: '/pods/',
        component: Layout,
        children: [{
            path: 'index/',
            name: 'pods',
            component: () => import('@/views/pods/index'),
            meta: { title: 'Pods', icon: 'box', roles: ['admin'] }
        }]
    },
    {
        path: '/storage',
        name: 'storage',
        component: Layout,
        children: [{
            path: 'storage',
            name: 'Storage',
            component: () => import('@/views/storage/index'),
            meta: { title: 'Storage', icon: 'storage', roles: ['admin'] }
        },
        {
            path: 'ide/',
            name: 'ide',
            hidden: true,
            component: () => import('@/views/storage/ide'),
            meta: { title: 'Web IDE' }
        }]
    },
    {
        path: '/registry',
        name: 'registry',
        component: Layout,
        children: [
            {
                path: 'repositories/',
                name: 'repositories',
                component: () => import('@/views/registry/index'),
                meta: { title: 'Repositories', icon: 'repository', roles: ['admin'] }
            }
            // {
            //     path: 'image/',
            //     name: 'image',
            //     hidden: true,
            //     component: () => import('@/views/registry/image'),
            //     meta: { title: 'Image', roles: ['admin'] }
            // }
        ]
    },
    {
        path: '/oauth/',
        meta: { title: 'OAuth', icon: 'oauth' },
        component: Layout,
        children: [
            {
                path: '',
                name: 'oauth',
                component: () => import('@/views/oauth/index'),
                meta: { title: 'OAuth', roles: ['admin'] }
            }
        ]
    },
    {
        path: '/grafana/',
        component: Layout,
        children: [
            {
                path: '',
                name: 'Grafana',
                component: () => import('@/views/grafana/index'),
                meta: { title: 'Grafana', icon: 'grafana', roles: ['admin'] }
            }
        ]
    }
];

const createRouter = () => new Router({
    mode: 'history', // require service support
    scrollBehavior: () => ({ y: 0 }),
    routes: constantRoutes.concat(asyncRoutes)
});

const router = createRouter();

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
    const newRouter = createRouter();
    router.matcher = newRouter.matcher; // reset router
}

export default router;
