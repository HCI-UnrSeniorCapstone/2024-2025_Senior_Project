<template>
    <div>
      <!-- Login Form -->
      <div v-if="!loggedIn">
        <v-form @submit.prevent="login">
          <v-text-field
            v-model="username"
            label="Username"
            :rules="[usernameRules]"
            required
          ></v-text-field>
          <v-text-field
            v-model="password"
            label="Password"
            type="password"
            :rules="[passwordRules]"
            required
          ></v-text-field>
          <v-btn color="primary" @click="login">Login</v-btn>
        </v-form>
      </div>
  
      <!-- Message and Data Display After Successful Login -->
      <div v-else>
        <p>Welcome, {{ user.username }}!</p>
        <v-btn color="secondary" @click="logout">Logout</v-btn>
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
    </div>
  </template>
  
  <script>
  import axios from 'axios'
  
  export default {
    name: 'TestDatabase',
    data() {
      return {
        msg: 'Please log in.',
        results: [], // Store the results from the database query
        username: '',
        password: '',
        loggedIn: false, // Boolean to track if the user is logged in
        user: {}, // Store the logged-in user's data
        usernameRules: [
          v => !!v || 'Username is required',
        ],
        passwordRules: [
          v => !!v || 'Password is required',
        ],
      }
    },
    methods: {
  // Handle login request
  login() {
  // Get the CSRF token from the meta tag or cookie
  const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  if (!csrfToken) {
    console.error('CSRF token not found');
    this.msg = 'CSRF token is missing';
    return;
  }

  const backendUrl = this.$backendUrl; // Ensure this is set correctly
  const path = `${backendUrl}/api/accounts/login`;

  // Send the login request with CSRF token in the headers
  axios.post(path, {
    email: this.username,
    password: this.password,
  }, {
    headers: {
      'X-CSRF-TOKEN': csrfToken,  // Attach CSRF token in the header
    }
  })
  .then(res => {
    this.loggedIn = true;
    this.user = res.data.user;  // Store logged-in user's data
    this.msg = 'Login successful';
    this.fetchData();  // Fetch data after successful login
  })
  .catch(error => {
    console.error('Error logging in:', error);
    this.msg = 'Login failed. Please check your credentials.';
  });
},


  // Fetch data from the backend after login
  fetchData() {
    const backendUrl = this.$backendUrl;
    const path = `${backendUrl}/test_db`;

    axios.get(path)
      .then(res => {
        if (Array.isArray(res.data)) {
          this.results = res.data;  // If data is an array, display the results
          console.log(this.results);
        } else {
          this.msg = 'Error: No data found or invalid response';
        }
      })
      .catch(error => {
        console.error('Error fetching test_db:', error);
        this.msg = 'Error connecting to the server';
      });
  },

  // Handle logout functionality
  logout() {
    this.loggedIn = false;
    this.user = {};
    this.results = [];
    this.username = '';
    this.password = '';
    this.msg = 'Logged out successfully';
  },
},

  }
  </script>
  
  <style scoped>
  /* Optionally add custom styles for the login form and data display */
  </style>
  