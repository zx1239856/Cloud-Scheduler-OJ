<template>
  <div class="container">
    <terminal class="terminal" :terminal="terminal" />
  </div>
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
    height: 100vh;
    width: 100vw;
}
</style>
