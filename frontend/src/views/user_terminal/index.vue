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
                url: 'user_terminals/?username=' + this.$route.query.username + '&token=' + this.$route.query.token + '&uuid=' + this.$route.query.uuid,
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
