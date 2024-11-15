<template>
  <div>
    <v-btn color="primary" @click="getMessage">{{ msg }}</v-btn>
  </div>
</template>
<script>
/*
NOTE: This is TEMP to show the connection to the server
*/
import axios from 'axios'
export default {
  name: 'PingServer',
  data() {
    return {
      msg: 'Hello!',
      // Default backend URL points to the server_backend
      backendUrl: 'http://100.91.135.16:5001',
    }
  },
  methods: {
    getMessage() {
      const path = `${this.backendUrl}/ping`
      axios
        .get(path)
        .then(res => {
          this.msg = res.data.message // Display the response message from server
        })
        .catch(error => {
          console.error('Error fetching ping:', error)
        })
    },
  },
  created() {
    this.getMessage()
  },
}
</script>
