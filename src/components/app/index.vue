<template>
  <div id="app">
    <section>
      <div v-if="socketState.isConnected" class="text-center text-info">
        Connected {{ socketState.connectionInfo }}
      </div>
      <div v-if="!socketState.isConnected" class="text-center text-danger">
        Not Connected {{ socketState.connectionError }}
      </div>

      <div class="text-center">
        <div v-if="errorMessage">
          <h1 class="text-danger">{{ errorMessage }}</h1>
        </div>
        <div class="row">
          <template v-for="data in uwsgi_data">
            <uwsgi-table :uwsgi_data="data"></uwsgi-table>
          </template>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import pkg from './../../../package.json';
import UwsgiTable from './../uwsgi-table/index.vue';

export default {
  components: {
    UwsgiTable
  },
  props: {
    name: String
  },

  created: function() {
    this.socketState = {
      isConnected: false,
      message: '',
      connectionError: "",
      connectionInfo: "",
    }

    this.$options.sockets.onerror = (message) => {
      this.uwsgi_data = []
      this.socketState.connectionError = "Connection error!!"
    }

    this.$options.sockets.onopen = (e) => {
      this.socketState.isConnected = true
      this.socketState.connectionInfo = `${e.target.url}`
    }

    this.$options.sockets.onclose = (e) => {
      this.socketState.isConnected = false
      this.uwsgi_data = []
      this.socketState.connectionError = `${e.target.url} closed.`
    }

    this.$options.sockets.onmessage = (message) => {
      var data = message.data
      if (!data || data == "") {
        data = {}
      }

      try {
        this.uwsgi_data = JSON.parse(data)
        this.errorMessage = ""
      } catch(e) {
        console.log("================")
        console.log("error JSON.parse")
        console.log(data)
        console.log("================")
      }
    }

    var socket = this.$socket
    setInterval(function(){
      socket.sendObj({action: "data"})
    }, 1000)

  },

  data () {
    return {
      name_: this.name || pkg.name,
      uwsgi_data: this.uwsgi_data || {},
      errorMessage: this.errorMessage,
      socketState: this.socketState
    }
  }
}

</script>
