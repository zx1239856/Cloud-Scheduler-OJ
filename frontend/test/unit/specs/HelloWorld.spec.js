import Vue from 'vue';
import HelloWorld from '@/components/HelloWorld';
import VueResource from 'vue-resource';

Vue.use(VueResource);

describe('HelloWorld.vue', () => {
    it('should render correct contents', () => {
        const Constructor = Vue.extend(HelloWorld);
        const vm = new Constructor().$mount();
        expect(vm.$el.querySelector('.hello h1').textContent)
            .toEqual('Welcome to Your Vue.js App');
    });
});
