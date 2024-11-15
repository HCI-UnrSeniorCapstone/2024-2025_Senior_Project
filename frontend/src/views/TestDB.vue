<template>
  <div>
    <v-btn color="primary" @click="getMessage">{{ msg }}</v-btn>
    <div v-if="results.length > 0">
      <h3>User Data:</h3>
      <ul>
        <li v-for="(user, index) in results" :key="index">
          ID: {{ user[0] }} | Name: {{ user[1] }} | Email: {{ user[2] }}
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No data found.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PingServer',
  data() {
    return {
      msg: 'Hello!',
      backendUrl: 'http://100.91.135.16:5001', // Backend server URL
      results: [], // Store the results from the database query
    }
  },
  methods: {
    getMessage() {
      const path = `${this.backendUrl}/test_db`
      axios
        .get(path)
        .then(res => {
          if (Array.isArray(res.data)) {
            this.results = res.data // If data is an array, display the results
            this.msg = 'Data fetched successfully'
          } else {
            this.msg = 'Error: No data found or invalid response'
          }
        })
        .catch(error => {
          console.error('Error fetching test_db:', error)
          this.msg = 'Error connecting to the server'
        })
    },
  },
  created() {
    this.getMessage()
  },
}
</script>
