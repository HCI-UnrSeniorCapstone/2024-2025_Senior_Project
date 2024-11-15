<script>
import axios from 'axios'

export default {
  name: 'Ping',
  data() {
    return {
      msg: 'Hello!',
      // Default backend URL points to the server_backend
      backendUrl: 'http://100.91.135.16:5001', // Server Backend for /ping route
    }
  },
  methods: {
    getMessage() {
      const path = `${this.backendUrl}/ping` // Always use the server_backend URL
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
    this.getMessage() // Call the server's ping route when the component is created
  },
}
</script>

<template>
  <div>
    <v-btn color="primary" @click="getMessage">{{ msg }}</v-btn>
  </div>
</template>
