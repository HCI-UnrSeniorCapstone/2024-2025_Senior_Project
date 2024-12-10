<template>
  <div>
    <p>Received Variable: {{ studyId }}</p>
  </div>
  <div class="container">
    <v-btn @click="startSession()" color="green">Begin Session</v-btn>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      studyId: null,
      participantSessId: null,
      study: null,
    }
  },

  mounted() {
    this.studyId = this.$route.params.id
    this.getStudyInfo()
  },

  methods: {
    // identical to fetchStudyData() on StudyPanel.vue
    // decided best to query using passed study id rather than send study object to this vue
    // we could miss recent changes to the study if we pass the obj, plus passing phat objects around isnt good
    async getStudyInfo() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/load_study/${this.studyId}`
        const response = await axios.get(path)

        this.study = response.data

        console.log(this.study)
      } catch (error) {
        console.error('Error fetching study details:', error)
      }
    },

    async getSessionID() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/create_participant_session/${this.studyId}`
        const response = await axios.get(path)
        this.participantSessId = response.data.participant_session_id
        console.log('Session ID: ', this.participantSessId)
        if (this.participantSessId) {
          // only allow the session to start and info the be passed to local flask if participant id is available
          this.study.participantSessId = this.participantSessId
          this.startSession()
        }
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
      }
    },

    async startSession() {
      try {
        const path = 'http://127.0.0.1:5001/run_study'
        const response = await axios.post(path, this.study)
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
      }
    },
  },
}
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
</style>
