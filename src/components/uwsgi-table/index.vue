<template>
  <div class="col-xs-12 col-md-6">
    <table class="table table-striped table-hover">
      <thead class="text-info">
        <tr>
          <th class="table-title" colspan="4">
            <span style="color:#fff">{{ uwsgi_data.socket_file }} </span>
          </th>
        </tr>
        <tr>
          <th style="width:70px">PID</th>
          <th style="width:70px">Status</th>
          <th>Info</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <template v-for="worker in getWorkers()">
          <tr v-bind:class="[(worker.status == 'busy') ? 'text-active' : '']">
            <td>{{ worker.pid }}</td>
            <td>{{ worker.status }}</td>
            <td>
              <div v-if="(worker.status == 'busy')">
                {{ worker.headers.REMOTE_ADDR }} -
                "{{ worker.headers.REQUEST_METHOD }} {{ worker.headers.HTTP_HOST }}{{ worker.headers.PATH_INFO }}"
              </div>
            </td>
            <td class="text-right">
              <div v-if="(worker.status == 'busy')">
                <a v-on:click="kill(uwsgi_data.socket_file, worker.pid, $event)" class="text-danger" href="#">kill</a>
              </div>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script>

export default {
  name: 'UwsgiTable',
  methods: {
    _getHeaders: function(worker) {
      var request = worker.cores[0]
      var httpHeaders = {}

      request.vars.forEach(function(v, i) {
        var kv = v.split("=")
        if (kv.length === 2) {
          httpHeaders[kv[0]] = kv[1]
        } else {
        }
      })
      return httpHeaders
    },

    show: function(worker) {
      var httpHeaders = this._getHeaders(worker)
    },

    getWorkers: function() {
      var workers = []

      if (!this.uwsgi_data.workers) { return workers }
      for (var i = 0; i < this.uwsgi_data.workers.length; i++) {
        var worker = this.uwsgi_data.workers[i]
        var headers = this._getHeaders(worker)
        worker.headers = headers
        workers.push(worker)
      }

      return workers
    },

    kill: function(socket, pid, e) {
      if (e) {
        e.preventDefault()
      }
      
      var command = {
        action: "kill",
        socket: socket,
        pid: pid
      }

      this.$socket.sendObj(command)
    }
  },
  props: {
    uwsgi_data: Object
  }
}

</script>
