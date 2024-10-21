<template>
  <v-app id="inspire">
    <v-app-bar
        color="primary"
    >
        <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>

        <v-app-bar-title>HCI Hub</v-app-bar-title>

        <template v-slot:append>
            <v-btn icon="mdi-dots-vertical"></v-btn>
        </template>
    </v-app-bar>

    <v-navigation-drawer
      v-model="drawer"
      temporary
    >
      <!--  -->
    </v-navigation-drawer>

    <v-main>
      <v-container>
        <v-row justify="center">
          <v-col cols="12" md="8">
            <form @submit.prevent="submit">
              <v-text-field
              v-model="name.value.value"
              :counter="10"
              :error-messages="name.errorMessage.value"
              label="Name"
              ></v-text-field>

              <v-text-field
              v-model="phone.value.value"
              :counter="7"
              :error-messages="phone.errorMessage.value"
              label="Phone Number"
              ></v-text-field>

              <v-text-field
              v-model="email.value.value"
              :error-messages="email.errorMessage.value"
              label="E-mail"
              ></v-text-field>

              <v-select
              v-model="select.value.value"
              :error-messages="select.errorMessage.value"
              :items="items"
              label="Select"
              ></v-select>

              <v-checkbox
              v-model="checkbox.value.value"
              :error-messages="checkbox.errorMessage.value"
              label="Mouse tracking"
              type="checkbox"
              value="1"
              ></v-checkbox>

              <v-btn
              class="me-4"
              type="submit"
              >
              submit
              </v-btn>

              <v-btn @click="handleReset">
              clear
              </v-btn>
            </form>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
  import { ref } from 'vue'
  import Button from './Button.vue'
  import { useField, useForm } from 'vee-validate'
  
  const { handleSubmit, handleReset } = useForm({
    validationSchema: {
      name (value) {
        if (value?.length >= 2) return true

        return 'Name needs to be at least 2 characters.'
      },
      phone (value) {
        if (/^[0-9-]{7,}$/.test(value)) return true

        return 'Phone number needs to be at least 7 digits.'
      },
      email (value) {
        if (/^[a-z0-9.-]+@[a-z0-9.-]+\.[a-z]+$/i.test(value)) return true

        return 'Must be a valid e-mail.'
      },
      select (value) {
        if (value) return true

        return 'Select an item.'
      },
      checkbox (value) {
        if (value === '1') return true

        return 'Must be checked.'
      },
    },
  })
  const name = useField('name')
  const phone = useField('phone')
  const email = useField('email')
  const select = useField('select')
  const checkbox = useField('checkbox')

  const items = ref([
    'Undergraduate Student',
    'Graduate Student',
    'Teacher',
    'Other',
  ])

  const submit = handleSubmit(values => {
    alert(JSON.stringify(values, null, 2))
  })
  const drawer = ref(null)
</script>


