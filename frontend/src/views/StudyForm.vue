<template>
  <v-main>
    <v-container class="mt-5">
      <v-row>
        <v-col cols="12" md="10">
          <form @submit.prevent="submit">
            <h2>Study Details</h2>
            <v-text-field
              v-model="studyName"
              :counter="25"
              label="Study Name *"
              :rules="studyNameRules"
            ></v-text-field>

            <v-text-field
              v-model="studyDescription"
              :counter="250"
              label="Study Description"
              :rules="studyDescriptionRules"
            ></v-text-field>

            <div class="flex-row">
              <v-select
                v-model="studyDesignType"
                :items="['Between', 'Within']"
                label="Study Design Type *"
                :rules="studyDesignTypeRules"
              ></v-select>

              <v-text-field
                v-model="participantCount"
                type="number"
                label="Expected # of Participants *"
                :rules="participantCountRules"
              ></v-text-field>
            </div>

            <h3>Tasks</h3>
            <v-expansion-panels multiple v-model="expandedTPanels">
              <v-expansion-panel v-for="(task, index) in tasks" :key="index">
                <v-expansion-panel-title @click="toggleTaskPanel(index)">
                  <template v-slot:default="{}">
                    <div
                      style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        width: 100%;
                      "
                    >
                      <span>{{ 'Task ' + (index + 1) }}</span>
                    </div>
                  </template>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <Task :ref="el => (taskRefs[index] = el)" :task="task" />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <div class="action-btns">
              <v-btn
                @click="addTaskFactor('task')"
                color="grey"
                class="add-rmv-btn"
              >
                +
              </v-btn>
              <v-btn
                @click="
                  displayDialog({
                    title: 'Remove Confirmation',
                    text: 'Are you sure you want to remove this task?',
                    source: 'task',
                  })
                "
                :disabled="!canRemoveTask"
                color="grey"
                class="add-rmv-btn"
              >
                -
              </v-btn>
            </div>

            <h3>Factors</h3>
            <v-expansion-panels multiple v-model="expandedFPanels">
              <v-expansion-panel
                v-for="(factor, index) in factors"
                :key="index"
              >
                <v-expansion-panel-title @click="toggleFactorPanel(index)">
                  <template v-slot:default="{}">
                    <div
                      style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        width: 100%;
                      "
                    >
                      <span>{{
                        'Factor ' + String.fromCharCode(65 + index)
                      }}</span>
                    </div>
                  </template>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <Factor
                    :ref="el => (factorRefs[index] = el)"
                    :factor="factor"
                  />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <div class="action-btns">
              <v-btn
                @click="addTaskFactor('factor')"
                color="grey"
                class="add-rmv-btn"
              >
                +
              </v-btn>
              <v-btn
                @click="
                  displayDialog({
                    title: 'Remove Confirmation',
                    text: 'Are you sure you want to remove this factor?',
                    source: 'factor',
                  })
                "
                :disabled="!canRemoveFactor"
                color="grey"
                class="add-rmv-btn"
              >
                -
              </v-btn>
            </div>

            <v-row class="btn-row" justify="center">
              <v-btn
                class="me-4 save-exit-btn"
                @click="
                  displayDialog({
                    title: 'Exit Confirmation',
                    text: 'Are you sure you want to exit before saving?',
                    source: 'exit',
                  })
                "
                >Exit</v-btn
              >
              <v-btn
                class="me-4 save-exit-btn"
                type="submit"
                :disabled="!isFormValid"
                >Save</v-btn
              >
            </v-row>
          </form>
        </v-col>
      </v-row>

      <div class="text-center pa-4">
        <v-dialog v-model="dialog" max-width="400" persistent>
          <v-card
            prepend-icon="mdi-alert-outline"
            :text="dialogDetails.text"
            :title="dialogDetails.title"
          >
            <template v-slot:actions>
              <v-spacer></v-spacer>

              <v-btn @click="closeDialog()"> Cancel </v-btn>

              <v-btn @click="closeDialog(dialogDetails.source)"> Agree </v-btn>
            </template>
          </v-card>
        </v-dialog>
      </div>
    </v-container>
  </v-main>

  <v-snackbar
    v-model="collapseError"
    :timeout="2000"
    color="red"
    variant="tonal"
  >
    {{ collapseErrorMsg }}
  </v-snackbar>
</template>

<script>
import Task from '../components/Task.vue'
import Factor from '../components/Factor.vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ref } from 'vue'

export default {
  components: { Task, Factor },

  setup() {
    const router = useRouter()
    const exit = () => {
      router.go(-1)
    }
    const factorRefs = ref([])
    const taskRefs = ref([])

    return { exit, taskRefs, factorRefs }
  },

  data() {
    return {
      studyName: '',
      studyDescription: '',
      studyDesignType: null,
      participantCount: '',
      // handle dynamic number of tasks/factors
      tasks: [],
      factors: [],
      // used to track the state of task & factor expansion panels
      expandedTPanels: [0],
      expandedFPanels: [0],
      // input validation for form fields (not tasks or factors)
      studyNameRules: [
        v => !!v || 'Study name is required.',
        v => v.length >= 2 || 'Study name must be at least 2 characters.',
        v => v.length <= 25 || 'Study name must be less than 25 characters.',
      ],
      studyDescriptionRules: [
        v =>
          v.length <= 250 ||
          'Study description must be less than 250 characters.',
      ],
      studyDesignTypeRules: [v => !!v || 'Must choose a study design type.'],
      participantCountRules: [v => v > 0 || 'Need at least 1 participant.'],
      // dialog box for user confirmation
      dialog: false,
      dialogDetails: {
        title: '',
        text: '',
        source: '',
      },
      // warning when trying to collapse improperly fileld panel
      collapseError: false,
      collapseErrorMsg: 'Cannot collapse with improperly filled field(s)',
    }
  },

  // view will load with 1 task and flask populated automatically
  mounted() {
    this.addTaskFactor('task')
    this.addTaskFactor('factor')
  },

  computed: {
    // fxn constantly checking if ALL fields are valid and used to disable save button until true
    isFormValid() {
      const studyNameCheck = this.studyNameRules.every(
        rule => rule(this.studyName) === true,
      )
      const studyDescCheck = this.studyDescriptionRules.every(
        rule => rule(this.studyDescription) === true,
      )
      const studyDesignCheck = this.studyDesignTypeRules.every(
        rule => rule(this.studyDesignType) === true,
      )
      const pCountCheck = this.participantCountRules.every(
        rule => rule(this.participantCount) === true,
      )

      // only validates expanded task panels since closed ones must already be in a valid state to collapse
      const tasksValid = this.expandedTPanels.every(index => {
        const taskRef = this.taskRefs[index]
        return taskRef?.validateTaskFields() ?? true
      })
      // same as above but for factors
      const factorsValid = this.expandedFPanels.every(index => {
        const factorRef = this.factorRefs[index]
        return factorRef?.validateFactorFields() ?? true
      })

      return (
        studyNameCheck &&
        studyDescCheck &&
        studyDesignCheck &&
        pCountCheck &&
        tasksValid &&
        factorsValid
      )
    },

    // min of 1 task required at all times, should disable delete/minus button if only 1 task currently
    canRemoveTask() {
      return this.tasks.length > 1
    },
    // min of 1 factor required
    canRemoveFactor() {
      return this.factors.length > 1
    },
  },

  methods: {
    addTaskFactor(type) {
      if (type == 'task') {
        this.tasks.push({
          taskName: '',
          taskDescription: '',
          taskDirections: '',
          taskDuration: '',
          measurementOptions: [],
        })
        // update expansion states and configuring new additions to start expanded
        const tIndex = this.tasks.length - 1
        this.expandedTPanels.push(tIndex)
      } else {
        this.factors.push({
          factorName: '',
          factorDescription: '',
        })
        // same expansion handling as above but for factors
        const fIndex = this.factors.length - 1
        this.expandedFPanels.push(fIndex)
      }
    },

    removeTaskFactor(type) {
      if (type == 'task') {
        const tIndex = this.tasks.length - 1
        this.tasks.pop()
        this.expandedTPanels = this.expandedTPanels.filter(i => i !== tIndex)
      } else if (type == 'factor') {
        const fIndex = this.factors.length - 1
        this.factors.pop()
        this.expandedFPanels = this.expandedFPanels.filter(i => i !== fIndex)
      }
    },

    // prevent task expansion panels from collapsing while input is invalid
    toggleTaskPanel(index) {
      const taskRef = this.taskRefs[index]
      if (taskRef && !taskRef.validateTaskFields()) {
        // if exists and input is invalid
        if (!this.expandedTPanels.includes(index)) {
          // and not already accounted for
          this.expandedTPanels.push(index) // add to array that tracks open task panels
          this.collapseError = true
        }
      } else if (taskRef && taskRef.validateTaskFields()) {
        this.expandedTPanels = this.expandedTPanels.filter(i => i !== index) // remove if valid, allowing panel to collapse
      }
    },

    // same as toggleTaskPanel() but for factors
    toggleFactorPanel(index) {
      const factorRef = this.factorRefs[index]
      if (factorRef && !factorRef.validateFactorFields()) {
        if (!this.expandedFPanels.includes(index)) {
          this.expandedFPanels.push(index)
          this.collapseError = true
        }
      } else if (factorRef && factorRef.validateFactorFields()) {
        this.expandedFPanels = this.expandedFPanels.filter(i => i !== index)
      }
    },

    // dynamic confirmation based on what button/action triggered it
    displayDialog(details) {
      this.dialogDetails = details
      this.dialog = true
    },

    // specialized action based on source of the dialog pop-up if "agree" is selected
    closeDialog(action) {
      if (action == 'task' || action == 'factor') {
        this.removeTaskFactor(action)
      } else if (action == 'exit') {
        this.exit()
      }
      this.dialog = false
    },

    submit() {
      const submissionData = {
        studyName: this.studyName,
        studyDescription: this.studyDescription,
        studyDesignType: this.studyDesignType,
        participantCount: this.participantCount,
        tasks: this.tasks.map(task => ({
          taskName: task.taskName,
          taskDescription: task.taskDescription,
          taskDirections: task.taskDirections,
          taskDuration: task.taskDuration,
          measurementOptions: [...task.measurementOptions],
        })),
        factors: this.factors.map(factor => ({
          factorName: factor.factorName,
          factorDescription: factor.factorDescription,
        })),
      }

      alert(JSON.stringify(submissionData, null, 2))
      console.log(JSON.stringify(submissionData, null, 2))
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/create_study`
        const response = axios.post(path, submissionData)
        console.log('Response:', response.data)
      } catch (error) {
        console.error('Error: ', error)
      }
    },
  },
}
</script>

<style scoped>
.btn-row {
  display: flex;
  margin-top: 50px;
}
.save-exit-btn {
  min-height: 40px;
  min-width: 125px;
}
.action-btns {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
  gap: 1px;
}
.add-rmv-btn {
  max-height: 25px;
  min-width: 25px;
  font-size: larger;
}
.flex-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}
</style>
