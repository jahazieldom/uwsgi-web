import Vue from 'vue';
import App from './components/app/index.vue';
import VueNativeSock from 'vue-native-websocket'

import './globals.css';

Vue.use(VueNativeSock, 'ws://127.0.0.1:6789/', { 
	format: 'json',
	reconnection: true,
	// reconnectionDelay: 3000,
})

new Vue({
  el: '#app',
  render: h => h(App)
});