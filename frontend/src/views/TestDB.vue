<template>
  <div>
    <v-btn color="primary" @click="getMessage">{{ msg }}</v-btn>
    <div v-if="results.length > 0">
      <h3>User Data:</h3>
      <ul>
        <li v-for="(user, index) in results" :key="index">
          Date Created: {{ user[0] }} | User Study Name: {{ user[1] }} |
          Description: {{ user[2] }} | Sessions: {{ user[3] }} | Role:
          {{ user[4] }}
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No data found.</p>
    </div>
  </div>
</template>

<script>

import api from '@/axiosInstance'

export default {
  name: 'TestDatabase',
  data() {
    return {
      msg: 'Hello!',
      results: [], // Store the results from the database query
    }
  },
  methods: {
    getMessage() {
      const path = `/test_db`
      api
        .get(path)
        .then(res => {
          if (Array.isArray(res.data)) {
            this.results = res.data // If data is an array, display the results
            console.log(this.results)
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
  mounted() {
    this.getMessage()
  },
}
</script>
