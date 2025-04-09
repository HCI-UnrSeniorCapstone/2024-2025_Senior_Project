<template>
  <v-app-bar color="primary">
    <v-app-bar-title>Fulcrum</v-app-bar-title>

    <v-spacer></v-spacer>

    <template v-if="!isAuthPage">
      <v-btn icon>
        <v-icon>mdi-bell-outline</v-icon>
      </v-btn>

      <v-btn icon>
        <v-icon>mdi-help-circle-outline</v-icon>
      </v-btn>

      <v-menu offset-y transition="slide-y-reverse">
        <template #activator="{ props }">
          <v-btn icon v-bind="props" size="large">
            <v-avatar color="primary" size="48">
              <v-icon size="32">mdi-account-circle</v-icon>
            </v-avatar>
          </v-btn>
        </template>

        <!-- (the card and menu content stays the same) -->
        <v-card style="min-width: 320px; padding: 8px;">
          <v-list-item class="px-4 py-3">
            <v-row align="center" no-gutters style="width: 100%">
              <v-col cols="auto">
                <v-avatar size="40">
                  <img src="https://randomuser.me/api/portraits/men/32.jpg" alt="User" />
                </v-avatar>
              </v-col>
              <v-col class="pl-3">
                <span class="text-subtitle-1 font-weight-medium">{{ displayName }}</span>
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
      </v-menu>
    </template>
  </v-app-bar>
</template>


<script>
import api from '@/axiosInstance'
export default {
  name: 'GlobalTopBar',
  data() {
    return {
      displayName: 'Loading...',
    };
  },
  computed: {
    isAuthPage() {
      return ['UserLogin', 'UserRegister', 'Confirmed'].includes(this.$route.name);
    }
  },
  watch: {
    '$route.name'(newRoute) {
      if (!['UserLogin', 'UserRegister', 'Confirmed'].includes(newRoute)) {
        this.fetchUserInfo();
      }
    }
  },
  methods: {
    goToProfile() {
      console.log('Go to Profile');
    },
    async logOut() {
      try {
        const response = await api.post('/accounts/logout', {}, {
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
        });

        if (response.status === 200) {
          console.log('Logged out successfully');
          this.$router.push({ name: 'UserLogin' });
        }
      } catch (err) {
        console.error('Error logging out:', err);
      }
    },
    async fetchUserInfo() {
      try {
        const response = await api.get('/accounts/get_user_profile_info', {
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
        });

        const user = response.data;
        const fullName = `${user.first_name || ''} ${user.last_name || ''}`.trim();
        this.displayName = fullName || user.email;

      } catch (err) {
        console.error('Error fetching user info:', err);
        this.displayName = 'User';
      }
    }
  },
  mounted() {
    if (!this.isAuthPage) {
      this.fetchUserInfo();
    }
  }
};
</script>
