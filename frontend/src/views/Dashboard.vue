<template>
  <v-container
    class="d-flex flex-column justify-center align-center fill-height transparent-bg"
    fluid
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

<!-- Leave this unscoped so it affects v-container properly -->
<style>
.fill-height {
  min-height: 100vh;
}
.transparent-bg {
  background-color: transparent !important;
}
</style>
