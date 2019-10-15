<template>
  <terminal class="terminal" :terminal="terminal" />
</template>

<script>
import Console from './Console';

export default {
    name: 'WebSSH',
    components: {
        'terminal': Console
    },
    data() {
        return {
            terminal: {
                pid: 1,
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
    width: 100%;
}
</style>
