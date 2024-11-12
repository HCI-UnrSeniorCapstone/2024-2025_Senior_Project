<template>
  <v-app>
    <v-main>
      <GlobalTopBar />
      <GlobalNavBar />
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
  import GlobalNavBar from '../components/GlobalNavBar.vue'
  import GlobalTopBar from '../components/GlobalTopBar.vue'

  export default {
    components: {
      GlobalNavBar,
      GlobalTopBar,
    },
  };
</script>