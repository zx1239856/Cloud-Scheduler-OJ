<template>
  <div id="no_vnc_screen" class="vnc-container">
    <div class="loading">
      <loading
        :active="isLoading"
        :can-cancel="false"
        :is-full-page="false"
        color="#fff"
        loader="dots"
        :width="200"
        :height="300"
      />
    </div>
  </div>
</template>

<script>
import Loading from 'vue-loading-overlay';
import RFB from '@novnc/novnc/core/rfb';
import getVNCPod from '@/api/vnc';

export default {
    name: 'VNC',
    components: {
        Loading
    },
    data() {
        return {
            uuid: this.$route.query.uuid,
            rfb: null,
            vnc_info: null,
            isLoading: true,
            retry: 0,
            polling: null
        };
    },
    mounted() {
        getVNCPod(this.uuid).then(response => {
            this.vnc_info = response.payload;
            this.connectVNC();
        });
    },
    beforeDestroy() {
        if (this.rfb) { this.rfb.disconnect(); }
        if (this.polling) { clearInterval(this.polling); this.polling = null; }
    },
    methods: {
        connectedToServer() {
            console.log('connected');
            this.isLoading = false;
            this.retry = 0;
            if (this.polling == null) {
                this.polling = setInterval(() => {
                    console.log('poll');
                    getVNCPod(this.uuid).then(response => {});
                }, 20 * 1000);
            }
        },
        disconnectedFromServer(msg) {
            this.isLoading = true;
            if (this.polling) { clearInterval(this.polling); this.polling = null; }
            if (this.retry < 50) {
                setTimeout(() => {
                    this.retry += 1;
                    this.connectVNC();
                }, 1000);
            }
        },
        connectVNC() {
            if (this.vnc_info != null) {
                const rfb = new RFB(
                    document.getElementById('no_vnc_screen'),
                    'wss://' + this.vnc_info.vnc_host + ':' + this.vnc_info.vnc_port + '/' + this.vnc_info.url_path,
                    {
                        credentials: { password: this.vnc_info.vnc_password }
                    }
                );
                rfb.addEventListener('connect', this.connectedToServer);
                rfb.addEventListener('disconnect', this.disconnectedFromServer);
                this.rfb = rfb;
            }
        }
    }
};
</script>

<style lang="scss">
.vnc-container {
    background: rgb(40, 40, 40);
    min-height: calc(100vh - 50px);
    display: flex;
    align-content: center;
    justify-content: center;

    div {
        height: auto !important;
    }

    .loading {
        position: absolute;
        svg {
            min-height: calc(100vh - 50px);
            display: flex;
            align-content: center;
            justify-content: center;
        }
    }
}
</style>
