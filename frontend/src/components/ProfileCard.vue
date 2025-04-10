<template>
  <v-card class="profile-card" elevation="2" rounded="xl">
    <v-img
      src="/images/unr n.jpg"
      alt="User profile"
      height="150"
      contain
      class="mb-4 rounded-circle"
    />

    <div class="text-center mb-4">
      <h3 class="text-h6 font-weight-bold mb-1">{{ fullName }}</h3>
      <p class="grey--text">{{ phone }}</p>
    </div>

    <v-divider class="mb-4" />

    <div class="info-section">
      <v-row dense>
        <v-col cols="12">
          <div class="info-label">Email</div>
          <div class="info-value">{{ email }}</div>
        </v-col>
      </v-row>
    </div>
  </v-card>
</template>

<script>
export default {
  props: {
    fullName: String,
    phone: String,
    email: String,
  },
}
</script>

<style scoped>
.profile-card {
  max-width: 400px;
  padding: 24px;
  background-color: white;
}
.rounded-circle {
  border-radius: 50%;
}
.info-section {
  padding: 0 8px;
}
.info-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
}
.info-value {
  font-size: 0.95rem;
  font-weight: 500;
}
</style>
