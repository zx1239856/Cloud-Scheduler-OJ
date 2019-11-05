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
                url: 'user_terminals/?identity=' + this.$route.query.identity,
                name: 'terminal',
                isPodSsh: false,
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
