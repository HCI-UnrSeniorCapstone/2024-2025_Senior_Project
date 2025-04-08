<template>
  <v-main>
    <v-container class="mt-5">
      <v-row>
        <v-col cols="12" md="10">
          <form @submit.prevent="submit">
            <h2>Session Setup (Facilitator)</h2>
            <v-divider></v-divider>
            <h3>Pair Task and Factors</h3>

            <v-container>
              <v-row
                v-for="(trial, index) in trials"
                :key="index"
                class="trial-group"
              >
                <v-col cols="12">
                  <h4 class="trial-header">Trial {{ index + 1 }}</h4>
                </v-col>

                <v-col cols="6">
                  <v-select
                    v-model="trial.taskID"
                    :items="taskOptions"
                    item-title="name"
                    item-value="id"
                    label="Select Task"
                  ></v-select>
                </v-col>
                <v-col cols="6">
                  <v-select
                    v-model="trial.factorID"
                    :items="factorOptions"
                    item-title="name"
                    item-value="id"
                    label="Select Factor"
                  ></v-select>
                </v-col>
              </v-row>

              <v-col class="action-btns" justify="end">
                <v-btn @click="addTrial()" color="grey" class="add-rmv-btn">
                  +
                </v-btn>
                <v-btn
                  :disabled="trials.length === 1"
                  @click="removeTrial()"
                  color="grey"
                  class="add-rmv-btn"
                >
                  -
                </v-btn>
              </v-col>
            </v-container>

            <v-row class="btn-row" justify="center">
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
                :disabled="
                  trials.length === 0 ||
                  trials.some(trial => !trial.taskID || !trial.factorID)
                "
                @click="
                  displayDialog({
                    title: 'Continue',
                    text: 'Are you sure you want to move on to the Participant Demographics Form?',
                    source: 'next',
                  })
                "
                color="success"
                >Next</v-btn
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
</template>

<script>

import api from '@/axiosInstance'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()
    const exit = () => {
      router.go(-1)
    }

    return { exit }
  },

  data() {
    return {
      studyId: null,
      study: null,
      formattedStudy: null,
      taskOptions: [],
      factorOptions: [],
      trials: [],
      dialog: false,
      dialogDetails: {
        title: '',
        text: '',
        source: '',
      },
    }
  },

  mounted() {
    this.studyId = this.$route.params.id
    this.getStudyInfo()
    this.addTrial()
  },

  methods: {
    // dynamic confirmation for canceling or moving to next part of session setup
    displayDialog(details) {
      this.dialogDetails = details
      this.dialog = true
    },

    // if they agree to exit we route elsewhere, if they click continue we route to next part
    closeDialog(source) {
      if (source == 'next') {
        this.formatStudy()
        this.goToParticipantForm()
      } else if (source == 'cancel') {
        this.exit()
      }
      this.dialog = false
    },

    addTrial() {
      this.trials.push({ taskID: null, factorID: null })
    },

    removeTrial() {
      this.trials.pop()
    },

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

    // Need so they can start putting together a trial sequence
    async getStudyInfo() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/load_study/${this.studyId}`
        const response = await api.get(path)

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

    // route to an empty study form page
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
.btn-row {
  display: flex;
  margin-top: 50px;
}
.cancel-next-btn {
  min-height: 40px;
  min-width: 200px;
}
.action-btns {
  display: flex;
  justify-content: flex-end;
  margin-top: 5px;
  gap: 1px;
}
.add-rmv-btn {
  max-height: 25px;
  min-width: 25px;
  font-size: larger;
}
.trial-group {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 5px;
}
.trial-header {
  font-weight: bold;
}
</style>
