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
                url: 'terminals/?shell=/bin/sh&pod=' + this.$route.query.pod + '&namespace=' + this.$route.query.namespace,
                name: 'terminal',
                isPodSsh: true,
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
