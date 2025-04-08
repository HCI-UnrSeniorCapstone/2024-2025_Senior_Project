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
      <v-alert v-if="error" type="error" class="mt-4">
        {{ error }}
      </v-alert>
    </v-form>
  </v-container>
</template>

<script>
import axios from 'axios'

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
        const response = await axios.post(
          `${this.$backendUrl}/api/accounts/login`,
          {
            email: this.email,
            password: this.password,
          },
          {
            headers: {
              Accept: 'application/json',
              'Content-Type': 'application/json',
            },
            withCredentials: true, 
          }
        )

        // Extract token from Flask-Security response
        const token =
          response.data.response?.user?.authentication_token ||
          response.data.authentication_token
          console.log('Login response:', response.data)

        if (token) {
          // Store token (you can use localStorage, cookies, Pinia, etc.)
          localStorage.setItem('auth_token', token)

          this.$router.push({ name: 'Dashboard' })
        } else {
          this.error = 'Login succeeded but no token returned.'
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
}
</script>

<style scoped>
.login-view {
  margin-top: 100px;
}
</style>
