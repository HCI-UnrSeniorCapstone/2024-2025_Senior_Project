<template>
  <div class="launcher_wrapper">
    <h2 class="mb-2">Session In Progress</h2>
    <p class="text-body-1 mb-6">
      Participant session has now started. You may minimize this window (DO NOT
      CLOSE) and launch the experiment in the external application. Return to
      this screen and press "Done" when finished.
    </p>
  </div>

  <CountdownTimer
    :duration="duration"
    :start="startCountdown"
    :description="description"
    @countdown-complete="allowToContinue"
  />

  <!-- Done button -->
  <v-row class="btn-row" justify="center" v-if="countdownComplete">
    <v-btn
      class="done-btn"
      :disabled="!countdownComplete"
      color="success"
      @click="$emit('submit')"
      >Done</v-btn
    >
  </v-row>
</template>

<script>
import CountdownTimer from '@/components/CountdownTimer.vue'
export default {
  name: 'SessionLaunch',
  emits: ['submit'],
  components: { CountdownTimer },
  props: {
    duration: {
      type: Number,
      default: 5,
    },
    startCountdown: {
      type: Boolean,
      default: false,
    },
    description: {
      type: String,
      default: 'About to begin',
    },
  },
  data() {
    return {
      countdownComplete: false,
    }
  },
  methods: {
    allowToContinue() {
      this.countdownComplete = true
    },
    async startSession() {
      try {
        const path = 'http://127.0.0.1:5001/run_study'
        const response = await api.post(path, this.sessionJson)
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
      }
    },
  },
}
</script>

<style scoped>
.launcher-wrapper {
  max-width: 600px;
  margin: 0 auto;
}
.btn-row {
  display: flex;
  margin-top: 50px;
}
.done-btn {
  min-height: 40px;
  min-width: 200px;
}
</style>
