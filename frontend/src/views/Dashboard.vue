<template>
  <v-container
    class="d-flex flex-column justify-center align-center"
    style="height: 100vh"
  >
    <v-skeleton-loader
      :loading="true"
      type="paragraph"
      style="width: 20vw; aspect-ratio: 5 / 1"
    >
    </v-skeleton-loader>

    <p class="mt-4 text-center" style="font-size: 1.2rem; color: #555">
      Coming soon!
    </p>
  </v-container>
</template>

<script>
export default {
  data() {
    return {}
  },
}
</script>

<style scoped>
.text-center {
  text-align: center;
}
.v-skeleton-loader {
  border-radius: 10px;
}
</style>
