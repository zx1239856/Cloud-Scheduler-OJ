<template>
  <div id="terminal" class="console" />
</template>

<style scoped>
* {
    margin: 0 !important;
    padding: 0;
    box-sizing: border-box;
}
</style>

<script>
// import Vue from 'vue'
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { AttachAddon } from 'xterm-addon-attach';
import store from '@/store';
import 'xterm/css/xterm.css';

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
        this.term = new Terminal({
            convertEol: true,
            fontFamily: `'Fira Mono', monospace`,
            rendererType: 'dom'
        });
        this.term.setOption('theme', {
            background: '#151942',
            foreground: '#FFF'
        });
        this.term.loadAddon(fitAddon);
        this.term.open(terminalContainer);
        fitAddon.fit();

        this.terminalSocket = new WebSocket(
            wsRoot + 'terminals/?shell=/bin/sh&pod=' + this.terminal.podName + '&namespace=' + this.terminal.namespace + '&cols=' + this.term.cols + '&rows=' + this.term.rows
        );
        this.terminalSocket.onopen = this.runRealTerminal;
        this.terminalSocket.onclose = this.closeRealTerminal;
        this.terminalSocket.onerror = this.errorRealTerminal;
        const attachAddon = new AttachAddon(this.terminalSocket);
        this.term.loadAddon(attachAddon);
        this.term._initialized = true;
    },
    beforeDestroy() {
        this.terminalSocket.close();
        this.term.dispose();
    },
    methods: {
        runRealTerminal() {
            this.terminalSocket.send(store.getters.name + '@' + store.getters.token);
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
