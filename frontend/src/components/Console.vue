<template>
    <div class="console" id="terminal"></div>
</template>

<style scoped>
* {
    margin: 0 !important;
    padding: 0;
    box-sizing: border-box;
}
#terminal {
    width: 100vw;
    height: 100vh;
}
</style>

<script>
import Vue from 'vue';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { AttachAddon } from 'xterm-addon-attach';

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
    },
    mounted() {
        console.log('pid : ' + this.terminal.pid + ' is on ready');
        let terminalContainer = document.getElementById('terminal');
        this.term = new Terminal();
        this.term.loadAddon(fitAddon);
        this.term.open(terminalContainer);
        fitAddon.fit();
        // open websocket
        this.terminalSocket = new WebSocket(
            Vue.http.options.ws_root +
                'terminals/?port=2223&host=inftyloop.tech&user=root&password=demoserver'
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
    }
};
</script>
