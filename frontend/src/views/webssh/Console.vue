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
const fitAddon = new FitAddon();
const wsRoot = process.env.VUE_APP_WS_API;

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

        this.terminalSocket = new WebSocket(
            wsRoot + 'terminals/?pod=wordpress-mysql-b9ddd6d4c-87cvq&shell=/bin/sh'
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
