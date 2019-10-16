<template>
  <terminal class="terminal" :terminal="terminal" />
</template>

<script>
import Console from '@/components/Console/index';

export default {
    name: 'WebSSH',
    components: {
        'terminal': Console
    },
    data() {
        return {
            terminal: {
                pid: 1,
                podName: this.$route.query.pod,
                namespace: this.$route.query.namespace,
                name: 'terminal',
                cols: 400,
                rows: 400
            }
        };
    }
};
</script>

<style lang="scss">
.terminal {
    min-height: inherit;
    height: 100%;
    width: 100%;
}
</style>
