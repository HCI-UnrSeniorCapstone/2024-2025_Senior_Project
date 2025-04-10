<template>
  <v-container fluid class="page-container">
    <v-slide-y-transition mode="in-out">
      <v-row justify="center" align="start" class="pt-10">
        <!-- Left: Profile Card -->
        <v-col cols="12" md="4">
          <ProfileCard
            :fullName="firstName + ' ' + lastName"
            :phone="userPhone"
            :email="email"
            @save="submit"
          />
        </v-col>

        <!-- Right: Editable Sections -->
        <v-col cols="12" md="6">
          <v-card class="pa-6 rounded-xl" elevation="2">
            <!-- Password Change -->
            <h2 class="text-h6 font-weight-bold mb-4">Change Password</h2>
            <form @submit.prevent="changePassword">
              <v-text-field
                v-model="currentPassword"
                label="Current Password"
                type="password"
                variant="filled"
                class="mb-4"
                required
              />

              <v-text-field
                v-model="newPassword"
                :type="showPassword ? 'text' : 'password'"
                label="New Password"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                required
                class="mb-4"
                hide-details="auto"
              />

              <v-text-field
                v-model="confirmNewPassword"
                :type="showPassword ? 'text' : 'password'"
                label="Confirm New Password"
                :error="showPasswordMismatch"
                :error-messages="
                  showPasswordMismatch ? ['Passwords do not match'] : []
                "
                required
                class="mb-4"
                hide-details="auto"
              />

              <v-btn
                :loading="changingPassword"
                :disabled="!passwordsMatch"
                color="primary"
                type="submit"
                variant="flat"
                class="rounded-pill px-6"
              >
                Change Password
              </v-btn>

              <v-alert
                v-if="passwordError"
                type="error"
                class="mt-2"
                variant="outlined"
                border="start"
              >
                <div class="alert-text">{{ passwordError }}</div>
              </v-alert>
            </form>

            <!-- Alerts -->
            <v-alert
              v-if="error"
              type="error"
              class="mt-4"
              variant="outlined"
              border="start"
            >
              <div class="alert-text">{{ error }}</div>
            </v-alert>

            <v-alert
              v-if="success"
              type="success"
              class="mt-4"
              variant="tonal"
              border="start"
            >
              <div class="alert-text">
                {{ successMessage || 'Update successful!' }}
              </div>
            </v-alert>
          </v-card>

          <!-- Logout Button -->
          <v-row justify="center" class="mt-6">
            <v-btn
              @click="logOut"
              color="primary"
              variant="flat"
              class="rounded-pill px-6"
            >
              Logout
            </v-btn>
          </v-row>
        </v-col>
      </v-row>
    </v-slide-y-transition>
  </v-container>
</template>

<script>
import api from '@/axiosInstance'
import ProfileCard from '@/components/ProfileCard.vue'

export default {
  name: 'UserProfile',
  components: { ProfileCard },
  data() {
    return {
      email: '',
      firstName: '',
      lastName: '',
      userPhone: '',
      loading: false,
      error: '',
      success: false,
      successMessage: '',

      // Password change
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: '',
      changingPassword: false,
      passwordError: '',
      showPassword: false,

      showCard: false,
    }
  },
  computed: {
    passwordsMatch() {
      return (
        this.newPassword === this.confirmNewPassword && this.newPassword !== ''
      )
    },
    showPasswordMismatch() {
      return (
        this.confirmNewPassword !== '' &&
        this.newPassword !== '' &&
        this.newPassword !== this.confirmNewPassword
      )
    },
  },
  mounted() {
    this.showCard = true
    this.loadUserInfo()
  },
  methods: {
    async loadUserInfo() {
      try {
        const res = await api.get('/accounts/get_user_profile_info')
        const user = res.data
        this.email = user.email
        this.firstName = user.first_name || ''
        this.lastName = user.last_name || ''
        this.userPhone = user.us_phone_number || ''
      } catch (err) {
        this.error = 'Failed to load user profile.'
        console.error(err)
      }
    },
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
          this.successMessage = 'Profile updated successfully.'
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
    async changePassword() {
      this.passwordError = ''
      this.success = false
      this.changingPassword = true

      if (!this.passwordsMatch) {
        this.passwordError = 'Passwords do not match.'
        this.changingPassword = false
        return
      }

      try {
        const res = await api.post('/accounts/change', {
          password: this.currentPassword,
          new_password: this.newPassword,
          new_password_confirm: this.confirmNewPassword,
        })

        if (res.status === 200) {
          this.success = true
          this.successMessage = 'Password changed successfully.'
          this.currentPassword = ''
          this.newPassword = ''
          this.confirmNewPassword = ''
        }
      } catch (err) {
        this.passwordError =
          err.response?.data?.response?.errors?.[0] ||
          err.response?.data?.error ||
          'Failed to change password.'
        console.error(err)
      } finally {
        this.changingPassword = false
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
.page-container {
  background: linear-gradient(to right, #f5f7fa, #c3cfe2);
  min-height: 100vh;
}
.alert-text {
  text-align: center;
  width: 100%;
  font-weight: 500;
}
</style>
