<template>
  <div class="container">
    <v-btn @click="startSession" color="green">Begin Session</v-btn>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    study: {
      // this is where we need to save the study passed from the study panel
      type: Object,
      required: true,
    },
  },

  data() {
    return {}
  },

  methods: {
    // needs to be modified
    async startSession() {
      try {
        const response = axios.post(
          'http://127.0.0.1:5001/run_study',
          this.study,
        ) //local flask
        console.log('Response:', response.data)
      } catch (error) {
        console.error('Error: ', error)
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
