<template>
  <div>
    <v-text-field
      v-model="task.taskName"
      :counter="25"
      label="Task Name *"
      :rules="taskNameRules"
    ></v-text-field>

    <v-text-field
      v-model="task.taskDescription"
      :counter="250"
      label="Task Description"
      :rules="taskDescriptionRules"
    ></v-text-field>

    <v-text-field
      v-model="task.taskDirections"
      :counter="250"
      label="Task Directions"
      :rules="taskDirectionsRules"
    ></v-text-field>

    <v-text-field
      v-model="task.taskDuration"
      type="number"
      label="Duration (min)"
      :rules="taskDurationRules"
    ></v-text-field>

    <div>
      <v-select
        v-model="task.measurementOptions"
        :items="updateVisibleMeasurementOptions"
        label="Measurement Options"
        chips
        multiple
      ></v-select>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    task: {
      type: Object,
      required: true,
      default: () => ({
        taskName: '',
        taskDescription: '',
        taskDirections: '',
        taskDuration: '',
        measurementOptions: [],
      }),
    },
  },

  data() {
    return {
      // validation rules for task-related inputs
      taskNameRules: [
        v => !!v || 'Task name is required.',
        v => v.length >= 2 || 'Task name must be at least 2 characters.',
        v => v.length <= 25 || 'Task name must be less than 25 characters.',
      ],
      taskDescriptionRules: [
        v =>
          v.length <= 250 ||
          'Task description must be less than 250 characters.',
      ],
      taskDirectionsRules: [
        v =>
          v.length <= 250 ||
          'Task directions must be less than 250 characters.',
      ],
      taskDurationRules: [
        v =>
          v === '' ||
          Number(v) > 0 ||
          'A set duration must be greater than 0 min.',
      ],
    }
  },

  methods: {
    validateTaskFields() {
      const taskNameCheck = this.taskNameRules.every(
        rule => rule(this.task.taskName) === true,
      )
      const taskDescCheck = this.taskDescriptionRules.every(
        rule => rule(this.task.taskDescription) === true,
      )
      const taskDirCheck = this.taskDirectionsRules.every(
        rule => rule(this.task.taskDirections) === true,
      )
      const taskDurCheck = this.taskDurationRules.every(
        rule => rule(this.task.taskDuration) === true,
      )
      return taskNameCheck && taskDescCheck && taskDirCheck && taskDurCheck
    },
  },

  // Used to remove Heat Map selection if Mouse Movement is deselected since it is dependent on it
  watch: {
    'task.measurementOptions'(newSelection) {
      if (!newSelection.includes('Mouse Movement')) {
        this.$emit('update:task', {
          ...this.task,
          measurementOptions: newSelection.filter(
            option => option !== 'Heat Map',
          ),
        })
      }
    },
  },

  // Changes selection options to include Heat Map when Mouse Movement is actively selected and vice versa
  computed: {
    updateVisibleMeasurementOptions() {
      if (this.task.measurementOptions.includes('Mouse Movement')) {
        return [
          // Heat Map should be visible since MM is selected
          'Mouse Movement',
          'Mouse Scrolls',
          'Mouse Clicks',
          'Keyboard Inputs',
          'Screen Recording',
          'Heat Map',
        ]
      } else {
        return [
          // Heat Map unavailable when Mouse Movement not selected
          'Mouse Movement',
          'Mouse Scrolls',
          'Mouse Clicks',
          'Keyboard Inputs',
          'Screen Recording',
        ]
      }
    },
  },
}
</script>
