<template>
    <v-container class="register-view" max-width="500px">
      <v-form @submit.prevent="register">
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
  
        <v-text-field
          v-model="firstName"
          label="First Name"
        ></v-text-field>
  
        <v-text-field
          v-model="lastName"
          label="Last Name"
        ></v-text-field>
  
        <v-btn
          :loading="loading"
          type="submit"
          color="primary"
          block
        >
          Register
        </v-btn>
  
        <v-alert v-if="error" type="error" class="mt-4 text-center">
        {{ error }}
        </v-alert>
  
        <v-alert v-if="success" type="success" class="mt-4 text-center">
        {{ success }}
        </v-alert>
      </v-form>
    </v-container>
  </template>
  
  <script>
  import axios from 'axios'
  
  export default {
    name: 'UserRegister',
    data() {
      return {
        email: '',
        password: '',
        firstName: '',
        lastName: '',
        loading: false,
        error: '',
        success: '',
      }
    },
    methods: {
      async register() {
        this.loading = true
        this.error = ''
        this.success = ''
  
        try {
          const response = await axios.post(
            `${this.$backendUrl}/api/accounts/register`,
            {
              email: this.email,
              password: this.password,
              first_name: this.firstName,
              last_name: this.lastName,
            },
            {
              headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
              },
            }
          )
  
          if (response.data.response?.user) {
            this.success = 'Registration successful! Please check your email to confirm.'
          } else {
            this.success = 'Registration submitted.'
          }
        } catch (err) {
            console.error(err)
            const errorData = err.response?.data;
            const response = errorData?.response;

            if (response?.errors && Array.isArray(response.errors)) {
                // Join all general errors into a single string
                this.error = response.errors.join(', ');
            } else if (typeof errorData === 'string') {
                this.error = errorData;
            } else {
                this.error = 'Registration failed. Please try again.';
            }
        } finally {
          this.loading = false
        }
      },
    },
  }
  </script>
  
  <style scoped>
  .register-view {
    margin-top: 80px;
  }
  </style>
  