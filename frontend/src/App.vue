<script setup>
import { RouterView } from 'vue-router'
import { useStudyStore } from '@/stores/study'

const studyStore = useStudyStore()
</script>

<template>
  <v-app>
    <v-main>
      <!--Use key from store so we can force-remount StudyForm.vue -->
      <RouterView :key="studyStore.formResetKey" />
    </v-main>
  </v-app>
</template>
