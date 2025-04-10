<template>
  <v-container fluid>
    <v-text-field
      :modelValue="email"
      label="Email"
      readonly
      variant="filled"
      class="mb-2"
    />
    <div class="email-note">
      This email is tied to your account and cannot be changed here.
    </div>

    <v-text-field
      :modelValue="firstName"
      @update:modelValue="$emit('update:firstName', $event)"
      label="First Name"
      variant="filled"
      class="mb-4"
    />

    <v-text-field
      :modelValue="lastName"
      @update:modelValue="$emit('update:lastName', $event)"
      label="Last Name"
      variant="filled"
      class="mb-4"
    />
  </v-container>
</template>

<script>
export default {
  props: {
    email: String,
    firstName: String,
    lastName: String,
  },
  emits: ['update:firstName', 'update:lastName'],
}
</script>

<style scoped>
.email-note {
  margin-bottom: 24px;
  font-size: 0.85rem;
  color: #777;
  font-style: italic;
}
</style>
