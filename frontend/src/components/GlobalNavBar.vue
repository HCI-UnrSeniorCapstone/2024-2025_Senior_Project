<template>
  <!-- Only render the drawer if the user is authenticated -->
  <v-navigation-drawer v-if="auth.isAuthenticated" expand-on-hover rail>
    <v-list density="compact" nav>
      <v-list-item
        to="/Dashboard"
        prepend-icon="mdi-view-dashboard-outline"
        title="Dashboard"
      ></v-list-item>
      <v-list-item
        @click="handleCreateNewStudy"
        prepend-icon="mdi-plus"
        title="Create New Study"
      ></v-list-item>

      <v-list-item
        to="/UserStudies"
        prepend-icon="mdi-form-select"
        title="User Studies"
      ></v-list-item>

      <v-list-item
        to="/DataAnalytics"
        prepend-icon="mdi-chart-box-outline"
        title="Data Analytics"
      ></v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { useRouter } from 'vue-router'
import { useStudyStore } from '@/stores/study'
import { auth } from '@/stores/auth'

export default {
  name: 'GlobalNavBar',
  setup() {
    const router = useRouter()
    const studyStore = useStudyStore()

    const handleCreateNewStudy = () => {
      studyStore.clearStudyID()
      studyStore.clearDrawerStudyID()
      studyStore.clearSessionID?.()
      studyStore.incrementFormResetKey() // Forces remount

      router.push({ name: 'StudyForm' })
    }

    return {
      auth,
      handleCreateNewStudy,
    }
  },
}
</script>
