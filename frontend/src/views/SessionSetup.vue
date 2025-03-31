<template>
  <v-main>
    <v-container class="mt-5 d-flex flex-column align-left">
      <h2 class="mb-6">Session Setup</h2>
      <v-row class="d-flex align-start" no-gutters>
        <!-- Trial Config Panel -->
        <v-col cols="12" md="5" class="pr-2">
          <v-card class="pa-4 trial-config-card" elevation="2">
            <h3 class="text-subtitle-1 font-weight-bold mb-2">
              Trial Configuration
            </h3>
            <div class="d-flex align-center gap-4">
              <!-- Trial count field -->
              <v-text-field
                v-model="selectedPermLength"
                label="Trial Count"
                type="number"
                min="1"
                max="100"
                class="flex-grow-1"
                @change="adjustTrialCount"
                :color="isRecLength ? 'warning' : 'primary'"
                :persistent-hint="isRecLength"
                hide-details
              >
              </v-text-field>
              <!-- Randomization btn -->
              <v-tooltip text="Generate Random Permutation">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon
                    @click="getPermutation"
                    color="transparent"
                    class="ml-2"
                  >
                    <v-icon>mdi-dice-6-outline</v-icon>
                  </v-btn>
                </template>
              </v-tooltip>
              <!-- Reset btn -->
              <v-tooltip text="Reset to Recommended">
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon
                    @click="resetCount"
                    color="transparent"
                    class="ml-2"
                  >
                    <v-icon>mdi-restart</v-icon>
                  </v-btn>
                </template>
              </v-tooltip>
            </div>

            <!-- Warning msg for recommended length -->
            <div v-if="isRecLength" class="text-warning text-caption mb-4">
              Recommended {{ recommendedPermLength }} trials for
              {{ recommendationReason }}
            </div>
          </v-card>
        </v-col>
        <!-- Trial coverage heatmap -->
        <v-col cols="12" md="7" class="pl-2">
          <v-card
            class="pa-8 d-flex flex-column justify-center align-center"
            elevation="2"
            style="height: 250px"
          >
            <coverage-heatmap
              :tasks="heatmapTasks"
              :factors="heatmapFactors"
              :trials="heatmapMatrix"
              :new-additions="updateNewPairsToHeatmap"
              :chart-height="200"
            />
          </v-card>
        </v-col>
      </v-row>

      <!-- Start of draggable trial cards section -->
      <h3 class="mt-0 mb-2">Pair Tasks & Factors</h3>
      <p
        v-if="study && study.studyDesignType == 'Between'"
        class="mb-2"
        style="color: #2164cf; font-weight: 500"
      >
        Factor selection synced across all trials for "Between" study type
      </p>
      <draggable
        v-model="trials"
        handle=".drag-handle"
        item-key="id"
        animation="200"
        class="w-100"
      >
        <template #item="{ element: trial, index }">
          <v-card
            class="pa-4 mt-2 mb-3 d-flex align-center trial-card"
            elevation="2"
          >
            <div
              class="position-absolute font-weight-bold"
              style="top: 8px; left: 16px; font-size: 16px"
            >
              Trial {{ index + 1 }}
            </div>
            <v-icon class="mr-4 drag-handle" color="grey darken-1"
              >mdi-drag</v-icon
            >
            <v-row>
              <v-col cols="6">
                <!-- Task dropdown -->
                <v-select
                  v-model="trial.taskID"
                  :items="taskOptions"
                  item-title="name"
                  item-value="id"
                  label="Select Task"
                  class="pt-5"
                  :error="!trial.taskID && formValidated"
                ></v-select>
              </v-col>
              <v-col cols="6">
                <!-- Factor dropdown -->
                <v-select
                  v-model="trial.factorID"
                  :items="factorOptions"
                  item-title="name"
                  item-value="id"
                  label="Select Factor"
                  class="pt-5"
                  :error="!trial.factorID && formValidated"
                  @update:modelValue="syncFactorsForBetween($event)"
                ></v-select>
              </v-col>
            </v-row>
            <!-- Delete trial btn -->
            <v-tooltip text="Delete trial">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-if="selectedPermLength > 1"
                  v-bind="props"
                  icon
                  @click="deleteTrial(index)"
                  color="transparent"
                  class="ml-2"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-tooltip>
          </v-card>
        </template>
      </draggable>

      <!-- Add new trial btn-->
      <v-btn
        variant="plain"
        color="grey darken-1"
        class="add-trial-btn"
        @click="addTrial"
        ><strong>+ Add Another Trial</strong></v-btn
      >

      <!-- Next and Cancel btns-->
      <v-row justify="center" class="btn-row">
        <v-btn
          class="me-4 cancel-next-btn"
          color="error"
          @click="
            displayDialog({
              title: 'Cancel Confirmation',
              text: 'Are you sure you want to exit the Session Setup page?',
              source: 'cancel',
            })
          "
          >Cancel</v-btn
        >
        <v-btn
          class="me-4 cancel-next-btn"
          @click="attemptToAdvance"
          :color="isFormIncomplete ? '#b7ccb2' : 'success'"
          >Next</v-btn
        >
      </v-row>

      <!-- Confirmation Dialog Pop-Up-->
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
</template>

<script>
import axios from 'axios'
import { useRouter } from 'vue-router'
import draggable from 'vuedraggable'
import CoverageHeatmap from '@/components/CoverageHeatmap.vue'

export default {
  setup() {
    const router = useRouter()
    const exit = () => {
      router.go(-1)
    }

    return { exit }
  },

  components: {
    draggable,
    CoverageHeatmap,
  },

  data() {
    return {
      studyId: null,
      study: null,
      formattedStudy: null,
      // Options that populate the dropdowns
      taskOptions: [],
      factorOptions: [],
      // Stores the currently defined trials
      trials: [],
      // Used for populating dialog pop-ups under diff conditions (ex. cancel vs next)
      dialog: false,
      dialogDetails: {
        title: '',
        text: '',
        source: '',
      },
      // Counts for the number of trials
      selectedPermLength: null,
      recommendedPermLength: null,
      recommendationReason: null, // Coverage or consistency
      formValidated: false,
      // Used for the trial heatmap
      heatmapMatrix: {},
      heatmapTasks: [],
      heatmapFactors: [],
    }
  },

  async mounted() {
    this.studyId = this.$route.params.id // Study ID passed from prev pg
    await this.getStudyInfo()
    await this.getRecPermLength()
    // Dynamically add trial cards to the pg immediately based on recommended count
    for (let i = 0; i < this.recommendedPermLength; i++) {
      this.addTrial()
    }
    this.selectedPermLength = this.recommendedPermLength
    // Another endpoint call, used to populate the trial coverage heatmap immediately
    this.getTrialOccurrences()
  },

  computed: {
    // Constant check to see if user deviates from recommended perm length
    isRecLength() {
      return this.selectedPermLength != this.recommendedPermLength
    },
    // Form invalid if there is not at least 1 trial or some fields are not filled
    isFormIncomplete() {
      return (
        this.trials.length === 0 ||
        this.trials.some(trial => !trial.taskID || !trial.factorID)
      )
    },
    // Used to update what the heatmap will show as trials are added/removed to the list of draggable trial cards
    updateNewPairsToHeatmap() {
      const definedTrials = []

      for (const trial of this.trials) {
        // Only consider trials that have both a task and factor selected
        if (!trial.taskID || !trial.factorID) {
          continue
        }
        // Get their corresponding names
        const taskName = this.taskOptions.find(t => t.id == trial.taskID)?.name
        const factorName = this.factorOptions.find(
          f => f.id == trial.factorID,
        )?.name
        definedTrials.push({ task: taskName, factor: factorName })
      }
      return definedTrials
    },
  },

  methods: {
    // Dynamic confirmation for canceling or moving to next part of session setup
    displayDialog(details) {
      this.dialogDetails = details
      this.dialog = true
    },

    // If they agree to canceling we route elsewhere & if they click continue we route to next part
    closeDialog(source) {
      if (source == 'next') {
        this.formatStudy()
        this.goToParticipantForm()
      } else if (source == 'cancel') {
        this.exit()
      }
      this.dialog = false
    },

    // Adding a trial
    addTrial() {
      this.trials.push({
        id: Date.now() + Math.random(),
        taskID: null,
        factorID: null,
      })
      this.selectedPermLength = this.trials.length
    },

    // Removes last trial
    removeTrial() {
      this.trials.pop()
      this.selectedPermLength = this.trials.length
    },

    // Deletes a trial at a specific index
    deleteTrial(index) {
      this.trials.splice(index, 1)
      this.selectedPermLength = this.trials.length
    },

    // Updating # of trials present to the recommended # from before
    resetCount() {
      this.selectedPermLength = this.recommendedPermLength
      this.adjustTrialCount()
    },

    // Handles the addition/removal of many trials at once
    adjustTrialCount() {
      const current_length = this.trials.length
      const new_length = Math.min(100, parseInt(this.selectedPermLength) || 1)

      this.selectedPermLength = new_length

      if (new_length < current_length) {
        for (let i = current_length; i > new_length; i--) {
          this.removeTrial()
        }
      } else if (new_length > current_length) {
        for (let i = current_length; i < new_length; i++) {
          this.addTrial()
        }
      }

      this.selectedPermLength = this.trials.length
    },

    // For Between studies, all trials have to have the same factor so if one field changes we update all for consistency
    syncFactorsForBetween(changedFactorID) {
      if (this.study.studyDesignType == 'Between') {
        this.trials = this.trials.map(t => ({
          ...t,
          factorID: changedFactorID,
        }))
      }
    },

    // Getting study JSON into proper format for passing to the local scripts
    formatStudy() {
      this.formattedStudy = {
        participantSessId: null,
        study_id: this.studyId,
        studyName: this.study.studyName,
        studyDescription: this.study.studyDescription,
        studyDesignType: this.study.studyDesignType,
        participantCount: this.study.participantCount,

        //Add trials array
        trials: this.trials.map(trial => ({
          taskID: trial.taskID,
          factorID: trial.factorID,
          startedAt: null,
        })),

        // Reformat tasks array to dict
        tasks: Object.fromEntries(
          this.study.tasks.map(task => [
            task.taskID.toString(),
            {
              measurementOptions: task.measurementOptions,
              taskDescription: task.taskDescription,
              taskDirections: task.taskDirections,
              taskDuration: task.taskDuration,
              taskName: task.taskName,
            },
          ]),
        ),

        // Reformat the same way for factors
        factors: Object.fromEntries(
          this.study.factors.map(factor => [
            factor.factorID.toString(),
            {
              factorDescription: factor.factorDescription,
              factorName: factor.factorName,
            },
          ]),
        ),
      }

      console.log('Formatted Study JSON:', this.formattedStudy)
    },

    // Retrieves all study details using passed study ID at page mount
    async getStudyInfo() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/load_study/${this.studyId}`
        const response = await axios.get(path)

        this.study = response.data

        console.log(this.study)

        this.taskOptions = this.study.tasks.map(task => ({
          id: task.taskID,
          name: task.taskName,
        }))
        this.factorOptions = this.study.factors.map(factor => ({
          id: factor.factorID,
          name: factor.factorName,
        }))
      } catch (error) {
        console.error('Error fetching study details:', error)
      }
    },

    // Determines what the recommended # of trials should be
    async getRecPermLength() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/previous_session_length/${this.studyId}`
        const response = await axios.get(path)

        const prevLength = response.data.prev_length

        if (prevLength == null) {
          // Study has no sessions currently so recommend a length with good coverage
          if (this.study.studyDesignType == 'Within') {
            // Perm of this length would hit all trial combos for Within study type
            this.recommendedPermLength =
              this.taskOptions.length * this.factorOptions.length
          } else {
            // Shorter because we only use 1 factor at a time for Between
            this.recommendedPermLength = this.taskOptions.length
          }
          this.recommendationReason = 'best trial coverage'
        } else {
          // Trial length should be the same as prior sessions for consistency (consider hard enforcing instead of recommending?)
          this.recommendedPermLength = prevLength
          this.recommendationReason = 'consistency with previous sessions'
        }
      } catch (error) {
        console.error('Error fetching study details:', error)
      }
    },

    // Generates a random set of trials for the user that is unique, "random", & balanced
    async getPermutation() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/get_new_trials_perm/${this.studyId}?trial_count=${this.selectedPermLength}`
        const response = await axios.get(path)

        console.log('Permutations response:', response.data)

        this.trials = []
        this.trials = response.data.new_perm.map(([taskID, factorID]) => ({
          taskID,
          factorID,
        }))
      } catch (error) {
        console.error('Error fetching random permutation:', error)
      }
    },

    // Retrieves occurences of trials (task-factor combos) in prior sessions (for the trial coverage heatmap)
    async getTrialOccurrences() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/get_trial_occurrences/${this.studyId}`
        const response = await axios.get(path)

        this.heatmapTasks = this.taskOptions.map(t => t.name)
        this.heatmapFactors = this.factorOptions.map(f => f.name)
        this.heatmapMatrix = response.data.matrix
      } catch (error) {
        console.error('Error fetching trial occurrences:', error)
      }
    },

    // Logic for whether the user clicking "Next" should work or not
    attemptToAdvance() {
      this.formValidated = true

      if (this.isFormIncomplete) {
        return
      } else {
        this.displayDialog({
          title: 'Continue',
          text: 'Are you sure you want to move on to the Participant Demographics Form?',
          source: 'next',
        })
      }
    },

    // Route to the next pg
    goToParticipantForm() {
      this.$router.push({
        name: 'SessionForm',
        query: { formattedStudy: JSON.stringify(this.formattedStudy) },
      })
    },
  },
}
</script>

<style scoped>
.trial-card {
  transition: transform 0.25s ease box-shadow 0.25s ease;
}
.trial-card:hover {
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
  background-color: #f0f0f0;
}
.drag-handle {
  cursor: grab;
}
.add-trial-btn {
  border-style: dashed !important;
  border-width: 2px !important;
  border-color: #9e9e9e !important;
  color: #616161 !important;
  width: 100%;
  min-height: 50px !important;
  text-transform: none;
}
.btn-row {
  display: flex;
  margin-top: 50px;
}
.cancel-next-btn {
  min-height: 40px;
  min-width: 200px;
}
.trial-config-card {
  height: 175px;
}
</style>
