<template>
  <div>
    <v-text-field
      v-model="task.taskName"
      :counter="25"
      label="Task Name *"
      :rules="nameRules"
      required
    ></v-text-field>

    <v-text-field
      v-model="task.taskDescription"
      :counter="250"
      label="Task Description"
      :rules="descRules"
    ></v-text-field>

    <v-text-field
      v-model="task.taskDuration"
      type="number"
      label="Duration (min)"
    ></v-text-field>

    <div class="flex-row">
      <v-combobox
        v-model="task.measurementTypes"
        :items="['Mouse Tracking', 'Mouse Scrolls', 'Mouse Clicks', 'Keyboard Inputs']"
        label="Measurement Options"
        chips
        multiple
      ></v-combobox>

      <v-btn icon @click="$emit('remove')" color="White">
        <v-icon>mdi-delete</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script setup>
  import { defineProps, defineEmits} from 'vue';

  const props = defineProps({
    task: Object,
  });
  const emits = defineEmits(['remove']);

  const nameRules = [
    v => !!v && v.length >= 2 || 'Task name must be at least 2 characters.',
    v => !!v && v.length <= 25 || 'Task name exceeds the character limit.'
  ];
  const descRules = [
    v => v.length <= 250 || 'Task description exceeds the character limit.',
  ]
</script>

<style scoped>
  .flex-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .v-combobox {
    flex-grow: 1;
    margin-right: 10px;
  }
  .v-btn {
    margin-bottom: 25px;
  }
  .task-break {
    margin-bottom: 20px;
  }
</style>