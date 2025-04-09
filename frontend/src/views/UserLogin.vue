<template>
  <v-container class="login-view" max-width="400px">
    <v-form @submit.prevent="login">
      <v-text-field
        v-model="email"
        label="Email"
        type="email"
        required
      ></v-text-field>

      <v-text-field
        v-model="password"
        label="Password"
        type="password"
        required
      ></v-text-field>

      <v-btn
        :loading="loading"
        color="primary"
        type="submit"
        block
      >
        Log In
      </v-btn>
      <v-row justify="center" class="mt-4">
  <v-col cols="12" class="text-center">
    <p>
      Don't have an account?
      <RouterLink to="/register" style="color: #1976D2;">Register here</RouterLink>
    </p>
  </v-col>
</v-row>
      <v-alert v-if="error" type="error" class="mt-4 center-text">
        {{ error }}
      </v-alert>
    </v-form>
  </v-container>
</template>

<script>
import api from '@/axiosInstance'
import Cookies from 'js-cookie'
import { pingServer } from '@/utility/ping'
export default {
  name: 'UserLogin',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: '',
    }
  },
  methods: {
    async login() {
  this.loading = true
  this.error = ''

  try {
    const response = await api.post(
      `/accounts/login`,
      {
        email: this.email,
        password: this.password,
      },
      {
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
        },
      }
    )

    console.log('Login response:', response.data)

    // If login works just redirect
    if (response.data.meta?.code === 200) {
      setTimeout(() => {
        this.$router.push({ name: 'Dashboard' })
      }, 500)
    } else {
      this.error = 'Login failed. Unexpected response.'
    }
  } catch (err) {
    console.error(err)
    this.error =
      err.response?.data?.error ||
      err.response?.data?.message ||
      'Login failed. Please check your credentials.'
  } finally {
    this.loading = false
  }
},
  },
  async mounted() {
    try {
      const response = await pingServer()
      if (response.status === 200) {
        // This prevents users from loading in login on their own
        // Now even if they did, there are protections to handle tokens
        // But this is a way to control the UI
        this.$router.push({ name: 'Dashboard' })
      }
    } catch (e) {
      // Don't redirect, just let user log in manually
    }
  },
}
</script>

<style scoped>
.login-view {
  margin-top: 100px;
}
.center-text {
  text-align: center;
}
</style>
