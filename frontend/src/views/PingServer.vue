<template>
  <div>
    <v-btn color="primary" @click="getMessage">{{ msg }}</v-btn>
  </div>
</template>
<script>
/*
NOTE: This is TEMP to show the connection to the server
*/
import api from '@/axiosInstance'
export default {
  name: 'PingServer',
  data() {
    return {
      msg: 'Hello!',
    }
  },
  methods: {
    getMessage() {
      const backendUrl = this.$backendUrl
      const path = `${backendUrl}/ping`
      api.get('/ping', {
  withCredentials: true,
  headers: {
    'Authentication-Token': localStorage.getItem('auth_token'),
  },
})
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
