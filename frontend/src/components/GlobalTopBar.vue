<template>
  <v-app-bar color="primary">
    <v-app-bar-title>Fulcrum</v-app-bar-title>

    <v-spacer></v-spacer>

    <!-- Always show About button -->
    <v-btn icon @click="goToAbout">
      <v-icon>mdi-help-circle-outline</v-icon>
    </v-btn>

    <!-- Only show if user is authenticated -->
    <template v-if="auth.isAuthenticated">
      <v-btn icon>
        <v-icon>mdi-bell-outline</v-icon>
      </v-btn>

      <v-menu offset-y transition="slide-y-transition">
        <template #activator="{ props }">
          <v-btn icon v-bind="props" size="large">
            <v-avatar color="primary" size="48">
              <v-icon size="32">mdi-account-circle</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <v-slide-y-transition mode="in-out">
          <v-card style="min-width: 320px; padding: 8px">
            <v-list-item class="px-4 py-3">
              <v-row align="center" no-gutters style="width: 100%">
                <v-col cols="auto">
                  <v-avatar size="40">
                    <img
                      src="/images/unr n.jpg"
                      alt="User"
                      style="
                        width: 100%;
                        height: 100%;
                        object-fit: cover;
                        border-radius: 50%;
                      "
                    />
                  </v-avatar>
                </v-col>
                <v-col class="pl-3">
                  <span class="text-subtitle-1 font-weight-medium">{{
                    displayName
                  }}</span>
                </v-col>
              </v-row>
            </v-list-item>

            <v-divider class="my-2" />

            <v-list>
              <v-list-item @click="goToProfile" class="px-4">
                <v-row align="center" no-gutters style="width: 100%">
                  <v-col cols="auto">
                    <v-icon>mdi-account</v-icon>
                  </v-col>
                  <v-col class="pl-3">
                    <span class="text-subtitle-2">Edit Profile</span>
                  </v-col>
                  <v-col cols="auto">
                    <v-icon>mdi-chevron-right</v-icon>
                  </v-col>
                </v-row>
              </v-list-item>

              <v-list-item @click="logOut" class="px-4">
                <v-row align="center" no-gutters style="width: 100%">
                  <v-col cols="auto">
                    <v-icon>mdi-logout</v-icon>
                  </v-col>
                  <v-col class="pl-3">
                    <span class="text-subtitle-2">Logout</span>
                  </v-col>
                  <v-col cols="auto">
                    <v-icon>mdi-chevron-right</v-icon>
                  </v-col>
                </v-row>
              </v-list-item>
            </v-list>
          </v-card>
        </v-slide-y-transition>
      </v-menu>
    </template>
  </v-app-bar>
</template>

<script>
import api from '@/axiosInstance'
import { auth } from '@/stores/auth'
import { useStudyStore } from '@/stores/study'
export default {
  name: 'GlobalTopBar',
  data() {
    return {
      displayName: 'Loading...',
      auth,
    }
  },
  watch: {
    'auth.user': {
      handler(newUser) {
        if (newUser) {
          const fullName =
            `${newUser.first_name || ''} ${newUser.last_name || ''}`.trim()
          this.displayName = fullName || newUser.email
        }
      },
      immediate: true, // Trigger immediately if auth.user is already set
    },
  },
  methods: {
    goToProfile() {
      this.$router.push({ name: 'UserProfile' })
    },
    goToAbout() {
      this.$router.push({ name: 'AboutPage' })
    },
    async logOut() {
      try {
        const response = await api.post('/accounts/logout')

        if (response.status === 200) {
          auth.isAuthenticated = false
          auth.user = null
          const studyStore = useStudyStore()
          studyStore.reset()
          this.$router.push({ name: 'UserLogin' })
        }
      } catch (err) {
        console.error('Error logging out:', err)
      }
    },
  },
}
</script>
