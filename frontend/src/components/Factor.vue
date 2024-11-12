<template>
  <div>
    <v-text-field
      v-model="factor.factorName"
      :counter="25"
      label="Factor Name *"
      :rules="factorNameRules"
    ></v-text-field>

    <div class="flex-row">
      <v-text-field
        v-model="factor.factorDescription"
        :counter="250"
        label="Factor Description"
        :rules="factorDescriptionRules"
      ></v-text-field>

      <v-btn icon @click="$emit('remove')" color="White" class="v-trash">
        <v-icon>mdi-delete</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script>

  export default {
    props: {
      factor: {
        type: Object,
        required: true,
        default: () => ({
          factorName: '',
          factorDescription: ''
        })
      }
    },

    data() {
      return {
        factorNameRules: [
          v => !!v || 'Factor name is required.',
          v => v.length >= 2 || 'Factor name must be at least 2 characters.',
          v => v.length <= 25 || 'Factor name must be less than 25 characters.'
        ],
        factorDescriptionRules: [
          v => v.length <= 250 || 'Factor description must be less than 250 characters.'
        ]
      };
    },

    methods: {

      validateFactorFields() {
        const factorNameCheck = this.factorNameRules.every(rule => rule(this.factor.factorName) === true);
        const factorDescCheck = this.factorDescriptionRules.every(rule => rule(this.factor.factorDescription) === true);
        return factorNameCheck && factorDescCheck;
      }
    }
  };
</script>

<style scoped>
  .flex-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .v-btn {
    margin-bottom: 25px;
  }
  .v-trash {
    margin-left: 25px;
  }
</style>
