<template>
  <div>
    <v-btn color="primary" @click="getSessionData">{{ msg }}</v-btn>

    <!-- Display the results if there is data -->
    <div v-if="Object.keys(results).length > 0">
      <h3>Session Data:</h3>
      <ul>
        <li v-for="(data, sessionId) in results" :key="sessionId">
          <strong>Dictionary Name:</strong> {{ sessionId }}
          <ul>
            <li v-for="(row, index) in data" :key="index">
              <pre>{{ row }}</pre>
            </li>
          </ul>
        </li>
      </ul>
    </div>

    <!-- Display a message if no results are found -->
    <div v-else>
      <p>No data found.</p>
    </div>
  </div>
</template>

<script>

import api from '@/axiosInstance'

export default {
  name: 'TestGetParticipantSessionCSVInfo',
  data() {
    return {
      msg: 'Fetch Session Data',
      results: {},
      studyId: 1,
      participantSessionId: 1,
    }
  },
  methods: {
    getSessionData() {
      const path = `/get_participant_session_data/${this.studyId}/${this.participantSessionId}`

      api
        .get(path)
        .then(res => {
          if (res.data && Object.keys(res.data).length > 0) {
            this.results = res.data
            this.msg = 'Data fetched successfully'
            console.log(this.results)
          } else {
            this.msg = 'Error: No data found or invalid response'
          }
        })
        .catch(error => {
          console.error('Error fetching session data:', error)
          this.msg = 'Error connecting to the server'
        })
    },
  },
  mounted() {
    this.getSessionData()
  },
}
</script>

<style scoped></style>
