<template>
  <div class="confirmed-view">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8" class="text-center">
          <h1 class="mb-4">Email Confirmation</h1>
          <p class="mb-2">
            <span v-if="isSuccess" style="color: green; font-size: 1.5rem;">✅</span>
            {{ confirmationMessage }}
          </p>
          <p v-if="isSuccess" class="mt-4">
            Redirecting to <router-link to="/UserLogin">login</router-link> in {{ countdown }} seconds...
          </p>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: 'ConfirmedView',
  data() {
    return {
      confirmationMessage: '',
      isSuccess: false,
      countdown: 4,
      countdownTimer: null,
    }
  },
  created() {
    const success = this.$route.query.success
    const error = this.$route.query.error

    if (success) {
      this.isSuccess = true
      this.confirmationMessage = success
      this.startCountdown()
    } else if (error) {
      this.confirmationMessage = `⚠️ ${error}`
    } else {
      this.confirmationMessage = 'Email already confirmed'
    }
  },
  methods: {
    startCountdown() {
      this.countdownTimer = setInterval(() => {
        if (this.countdown > 1) {
          this.countdown--
        } else {
          clearInterval(this.countdownTimer)
          this.$router.push('/UserLogin')
        }
      }, 1000)
    },
  },
  beforeDestroy() {
    if (this.countdownTimer) clearInterval(this.countdownTimer)
  },
}
</script>

<style scoped>
.confirmed-view {
  padding: 2rem;
  text-align: center;
}
</style>
