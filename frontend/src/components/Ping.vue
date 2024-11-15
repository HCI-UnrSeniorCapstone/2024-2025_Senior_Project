<script>
import axios from 'axios'

export default {
  name: 'Ping',
  data() {
    return {
      msg: 'Hello!',
      backendUrl: 'http://100.91.135.16:5001', // Always point to the server_backend
    }
  },
  methods: {
    getMessage() {
      const path = `${this.backendUrl}/ping` // Always use server_backend
      axios
        .get(path)
        .then(res => {
          this.msg = res.data.message // Display the response message
        })
        .catch(error => {
          console.error(error)
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
