<template>
  <v-main>
    <v-container class="mt-5">
      <v-row>
        <v-col cols="12" md="10">
          <form @submit.prevent="submit">
            <!-- Title -->
            <h2 class="text-h6 font-weight-bold mb-2">Profile Information</h2>

            <!-- Profile Info Card -->
            <v-card class="pa-4 mb-6">
              <ProfileDetails
                :email="email"
                v-model:firstName="firstName"
                v-model:lastName="lastName"
              />
            </v-card>

            <!-- Buttons Row -->
            <v-row class="btn-row" justify="center">
              <v-btn
                @click="logOut"
                color="primary"
                variant="flat"
                class="me-4 save-exit-btn rounded-pill px-6"
              >
                Logout
              </v-btn>
              <v-btn
                :loading="loading"
                color="primary"
                type="submit"
                variant="tonal"
                class="save-exit-btn rounded-pill px-6"
              >
                Save Changes
              </v-btn>
            </v-row>

            <!-- Change Email -->
            <v-card class="pa-4 mt-6 mb-4">
              <h3 class="text-subtitle-1 font-weight-medium mb-3">
                Change Email
              </h3>
              <v-text-field
                v-model="newEmail"
                label="New Email"
                variant="filled"
                class="mb-2"
              />
              <v-btn
                :loading="changingEmail"
                color="primary"
                variant="flat"
                class="rounded-pill px-6"
                @click="changeEmail"
              >
                Change Email
              </v-btn>
            </v-card>

            <!-- Reset Password -->
            <v-card class="pa-4 mb-4">
              <h3 class="text-subtitle-1 font-weight-medium mb-3">
                Reset Password
              </h3>
              <p class="mb-2">
                Click below to receive a password reset link via email.
              </p>
              <v-btn
                :loading="sendingReset"
                color="primary"
                variant="flat"
                class="rounded-pill px-6"
                @click="requestPasswordReset"
              >
                Send Reset Email
              </v-btn>
            </v-card>

            <!-- Alerts -->
            <v-alert
              v-if="error"
              type="error"
              class="mt-4 top-alert"
              variant="outlined"
              border="start"
            >
              <div class="alert-text">{{ error }}</div>
            </v-alert>

            <v-alert
              v-if="success"
              type="success"
              class="mt-4 top-alert"
              variant="tonal"
              border="start"
            >
              <div class="alert-text">
                {{ successMessage || 'Update successful!' }}
              </div>
            </v-alert>
          </form>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script>
import api from '@/axiosInstance'
import ProfileDetails from '@/components/ProfileDetails.vue'

export default {
  name: 'UserProfile',
  components: { ProfileDetails },
  data() {
    return {
      email: '',
      firstName: '',
      lastName: '',
      loading: false,
      error: '',
      success: false,
      newEmail: '',
      changingEmail: false,
      sendingReset: false,
      successMessage: '',
    }
  },
  async mounted() {
    try {
      const res = await api.get('/accounts/get_user_profile_info')
      const user = res.data
      this.email = user.email
      this.firstName = user.first_name || ''
      this.lastName = user.last_name || ''
    } catch (err) {
      this.error = 'Failed to load user profile.'
      console.error(err)
    }
  },
  methods: {
    async submit() {
      this.error = ''
      this.success = false
      this.loading = true

      try {
        const payload = {
          first_name: this.firstName,
          last_name: this.lastName,
        }

        const res = await api.post('/accounts/update_user_profile', payload)

        if (res.status === 200) {
          this.success = true
        }
      } catch (err) {
        this.error =
          err.response?.data?.error ||
          err.response?.data?.message ||
          'Failed to update profile.'
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async changeEmail() {
      this.error = ''
      this.success = false
      this.changingEmail = true

      try {
        const res = await api.post('/accounts/change-email', {
          email: this.newEmail,
        })

        if (res.status === 200) {
          this.success = true
          this.successMessage = 'Confirmation email sent to ' + this.newEmail
          this.newEmail = ''
        }
      } catch (err) {
        this.error =
          err.response?.data?.error ||
          err.response?.data?.message ||
          'Failed to change email.'
        console.error(err)
      } finally {
        this.changingEmail = false
      }
    },
    async requestPasswordReset() {
      this.error = ''
      this.success = false
      this.sendingReset = true

      try {
        const res = await api.post('/accounts/reset', {
          email: this.email,
        })

        if (res.status === 200) {
          this.success = true
        }
      } catch (err) {
        this.error =
          err.response?.data?.error ||
          err.response?.data?.message ||
          'Failed to send reset email.'
        console.error(err)
      } finally {
        this.sendingReset = false
      }
    },
    async logOut() {
      try {
        const res = await api.post('/accounts/logout')
        if (res.status === 200) {
          this.$router.push({ name: 'UserLogin' })
        }
      } catch (err) {
        console.error('Logout failed:', err)
      }
    },
  },
}
</script>

<style scoped>
.btn-row {
  display: flex;
  margin-top: 50px;
}
.save-exit-btn {
  min-height: 40px;
  min-width: 125px;
}
.top-alert {
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}
.alert-text {
  text-align: center;
  width: 100%;
  font-weight: 500;
}
</style>
