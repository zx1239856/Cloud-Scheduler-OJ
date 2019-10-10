<template>
  <div id="terminal" class="console" />
</template>

<style scoped>
* {
    margin: 0 !important;
    padding: 0;
    box-sizing: border-box;
}
#terminal {
    width: 100%;
    height: 100%;
}
</style>

<script>
// import Vue from 'vue'
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { AttachAddon } from 'xterm-addon-attach';
import Config from '../../config';
const fitAddon = new FitAddon();

export default {
    name: 'Console',
    props: {
        terminal: {
            type: Object,
            default: () => {}
        }
    },
    data() {
        return {
            term: null,
            terminalSocket: null
        };
    },
    mounted() {
        console.log('pid : ' + this.terminal.pid + ' is on ready');
        const terminalContainer = document.getElementById('terminal');
        this.term = new Terminal();
        this.term.loadAddon(fitAddon);
        this.term.open(terminalContainer);
        fitAddon.fit();
        // open websocket
        const root = (process.env.NODE_ENV === 'production' ? Config.prod.wsUrl : Config.dev.wsUrl);

        this.terminalSocket = new WebSocket(
            //   Vue.http.options.ws_root +
            root + 'terminals/?port=2223&host=inftyloop.tech&user=root&password=demoserver'
        );
        this.terminalSocket.onopen = this.runRealTerminal;
        this.terminalSocket.onclose = this.closeRealTerminal;
        this.terminalSocket.onerror = this.errorRealTerminal;
        const attachAddon = new AttachAddon(this.terminalSocket);
        this.term.loadAddon(attachAddon);
        this.term._initialized = true;
        console.log('mounted is going on');
    },
    beforeDestroy() {
        this.terminalSocket.close();
        this.term.destroy();
    },
    methods: {
        runRealTerminal() {
            console.log('webSocket is finished');
        },
        errorRealTerminal() {
            console.log('error');
        },
        closeRealTerminal() {
            console.log('close');
        }
    }
};
</script>
