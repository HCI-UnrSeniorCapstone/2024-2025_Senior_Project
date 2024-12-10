<template>
  <v-main>
    <v-container class="mt-5">
      <v-row v-if="showForm">
        <v-col cols="12" md="10">
          <form @submit.prevent="submit">
            <h2>Participant Information</h2>
            <v-text-field
              v-model="participantAge"
              type="number"
              label="Age *"
              :rules="participantAgeRules"
            ></v-text-field>

            <v-select
              v-model="participantGender"
              :items="[
                'Male',
                'Female',
                'Non-Binary',
                'Other',
                'Prefer Not to Say',
              ]"
              label="Gender *"
              :rules="participantGenderRules"
              :menu-props="{ maxHeight: '200px', offsetY: true }"
            ></v-select>
            <div>
              <v-select
                v-model="participantRaceEthnicity"
                :items="[
                  'American Indian or Alaska Native',
                  'Asian',
                  'Black or African American',
                  'Hispanic or Latino',
                  'Native Hawaiian or Other Pacific Islander',
                  'White',
                ]"
                label="Race/Ethnicity *"
                :rules="participantRaceEthnicityRules"
                multiple
                chips
                :menu-props="{ maxHeight: '200px', offsetY: true }"
              ></v-select>
            </div>
            <v-select
              v-model="participantEducationLv"
              :items="[
                'Some High School',
                'High School Graduate or Equivalent',
                'Some College',
                'Associate\'s Degree',
                'Bachelor\'s Degree',
                'Master\'s Degree',
                'Doctorate',
              ]"
              label="Education Level *"
              :rules="participantEducationLvRules"
              :menu-props="{ maxHeight: '200px', offsetY: true }"
            ></v-select>

            <v-text-field
              v-model="participantTechCompetency"
              type="number"
              label="Technology Competency (1-10) *"
              :rules="participantTechCompetencyRules"
              :menu-props="{ maxHeight: '200px', offsetY: true }"
            ></v-text-field>

            <v-row class="btn-row" justify="center">
              <v-btn
                class="me-4 cancel-begin-btn"
                color="error"
                @click="
                  displayDialog({
                    title: 'Cancel Confirmation',
                    text: 'Are you sure you want to exit this current session?',
                    source: 'cancel',
                  })
                "
                >Cancel</v-btn
              >
              <v-btn
                class="me-4 cancel-begin-btn"
                type="submit"
                :disabled="!isFormValid"
                @click="
                  displayDialog({
                    title: 'Begin Session Confirmation',
                    text: 'Are you sure you want to begin the session?',
                    source: 'begin',
                  })
                "
                color="success"
                >Begin Session</v-btn
              >
            </v-row>
          </form>
        </v-col>
      </v-row>

      <div v-else class="timer-counter">
        <v-progress-circular
          :model-value="progressTimer"
          :size="150"
          :width="15"
          color="primary"
        >
        </v-progress-circular>
        <div class="timer-msgs">
          <p class="timer-msg">Session starting in {{ timer }} seconds...</p>
          <p class="timer-mini-msg">
            Minimize the window now and open the experiment
          </p>
          <v-btn
            v-if="resultsAvailable"
            class="me-4 res-btn"
            color="secondary"
            @click="goToResults()"
            >View Results</v-btn
          >
        </div>
      </div>
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
      showForm: true,
      timer: 15,
      timerInterval: null,
      resultsAvailable: false,
      studyId: null,
      participantSessId: null,
      study: null,
      // participant form fields
      participantAge: '',
      participantGender: '',
      participantRaceEthnicity: [],
      participantEducationLv: '',
      participantTechCompetency: '',
      // form field rules
      participantAgeRules: [
        v => v !== '' || 'Required field.',
        v => Number(v) > 0 || 'Valid inputs must be a number greater than 0.',
      ],
      participantGenderRules: [v => !!v || 'Required field.'],
      participantRaceEthnicityRules: [
        v =>
          (Array.isArray(v) && v.length > 0) ||
          'Must choose at least one option provided.',
      ],
      participantEducationLvRules: [v => !!v || 'Required field.'],
      participantTechCompetencyRules: [
        v => v !== '' || 'Required field.',
        v =>
          (Number(v) >= 1 && Number(v) <= 10) ||
          'Valid inputs must be a number between 1 and 10.',
      ],
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
  },

  computed: {
    // fxn always checking field inputs and won't allow a session form to be saved
    isFormValid() {
      const ageCheck = this.participantAgeRules.every(
        rule => rule(this.participantAge) === true,
      )
      const genderCheck = this.participantGenderRules.every(
        rule => rule(this.participantGender) === true,
      )
      const raceEthnicityCheck = this.participantRaceEthnicityRules.every(
        rule => rule(this.participantRaceEthnicity) === true,
      )
      const edLvCheck = this.participantEducationLvRules.every(
        rule => rule(this.participantEducationLv) === true,
      )
      const techCompCheck = this.participantTechCompetencyRules.every(
        rule => rule(this.participantTechCompetency) === true,
      )

      return (
        ageCheck &&
        genderCheck &&
        raceEthnicityCheck &&
        edLvCheck &&
        techCompCheck
      )
    },

    progressTimer() {
      return (this.timer / 15) * 100
    },
  },

  methods: {
    // dynamic confirmation for canceling or beginning the session
    displayDialog(details) {
      this.dialogDetails = details
      this.dialog = true
    },

    // if they agree to exit we route elsewhere, if they agree to start we notify they can close window and start session
    closeDialog(source) {
      if (source == 'begin') {
        this.sessionStarted()
      } else if (source == 'cancel') {
        this.exit()
      }
      this.dialog = false
    },

    // when a session is initiated and confirmed the form should go away and instead tell the user they can minimize the website to open their experiment
    sessionStarted() {
      this.showForm = false
      this.timerInterval = setInterval(() => {
        if (this.timer > 0) {
          this.timer -= 1
        } else {
          clearInterval(this.timerInterval)
          this.getSessionID()
          this.resultsAvailable = true
        }
      }, 1000)
    },

    goToResults() {
      this.$router.push({
        name: 'SessionReporting',
        params: { id: this.participantSessId },
      })
    },

    // identical to fetchStudyData() on StudyPanel.vue
    // decided best to query using passed study id rather than send study object to this vue
    // we could miss recent changes to the study if we pass the obj, plus passing phat objects around isnt good
    async getStudyInfo() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/load_study/${this.studyId}`
        const response = await axios.get(path)

        this.study = response.data

        console.log(this.study)
      } catch (error) {
        console.error('Error fetching study details:', error)
      }
    },

    async getSessionID() {
      try {
        const submissionData = {
          participantGender: this.participantGender,
          participantEducationLv: this.participantEducationLv,
          participantAge: this.participantAge,
          participantRaceEthnicity: this.participantRaceEthnicity,
          participantTechCompetency: this.participantTechCompetency,
        }
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/create_participant_session/${this.studyId}`
        const response = await axios.post(path, submissionData)
        this.participantSessId = response.data.participant_session_id
        console.log('Session ID: ', this.participantSessId)
        if (this.participantSessId) {
          // only allow the session to start and info the be passed to local flask if participant id is available
          this.study.participantSessId = this.participantSessId
          this.study.study_id = this.studyId
          this.startSession()
          this.viewResultsBtt = true

          //********* WORK IN PROGRESS ******************************//
          // const default_measurment_id = {"Mouse Movement": 1, "Mouse Scrolls": 2, "Mouse Clicks": 3, "Keyboard Inputs": 4}
          // console.log(this.study.tasks[0].taskName) //gets the task name
          // console.log(this.study.factors[0].factorName) //gets factor name
          // console.log(this.study.tasks[0].measurementOptions[0]) //gets the measurment name
          //participantSessId
          //study_id
          // console.log(this.study.tasks[0].taskID) //gets the task id
          // console.log(default_measurment_id["Mouse Scrolls"]) //gets the measurment id
          // console.log(this.study.factors[0].factorID) //gets the factor id

          // for(let i = 0; i < this.study.tasks.length; i++){
          //   console.log(this.study.tasks[i].measurementOptions[i])
          //   if(this.study.tasks[i].measurementOptions[i] == 'Mouse Scrolls' || this.study.tasks[i].measurementOptions[i] == 'Mouse Movement' || this.study.tasks[i].measurementOptions[i] == 'Mouse Clicks'){
          //     const csv_path = `./${this.study.tasks[i].taskName}_${this.study.factors[i].factorName}_${this.study.tasks[i].measurementOptions[i]}_${this.study.participantSessId}_${this.study.study_id}_${this.study.tasks[i].taskID}_${default_measurment_id['Mouse Scrolls']}_${this.study.factors[i].factorID}.csv`
          //     console.log(csv_path)

          //     const file = new File([this.getFileBlob_mouse(csv_path)], 'file.csv', { type: 'text/csv' })

          //     const formData = new FormData()
          //     formData.append('input_csv', this.file) // Append the selected file

          //     const backendUrl = this.$backendUrl
          //     const path = `${backendUrl}/save_session_data_instance/${this.study.participantSessId}/${this.study.study_id}/${this.study.tasks[i].taskID}/${default_measurment_id[this.study.tasks[i].measurementOptions[i]]}/${this.study.factors[i].factorID}`
          //     axios
          //       .post(path, formData, {
          //         headers: {
          //           'Content-Type': 'multipart/form-data',
          //         },
          //       })
          //   }
          //   else if (this.study.tasks[i].measurementOptions[i] == 'Keyboard Inputs'){
          //     const csv_path = `./${this.study.tasks[i].taskName}_${this.study.factors[i].factorName}_${this.study.tasks[i].measurementOptions[i]}_${this.study.participantSessId}_${this.study.study_id}_${this.study.tasks[i].taskID}_${default_measurment_id['Keyboard Inputs']}_${this.study.factors[i].factorID}.csv`
          //     console.log(csv_path)

          //     const file = new File([this.getFileBlob_mouse(csv_path)], 'file.csv', { type: 'text/csv' })

          //     const formData = new FormData()
          //     formData.append('input_csv', this.file)

          //     const backendUrl = this.$backendUrl
          //     const path = `${backendUrl}/save_session_data_instance/${this.study.participantSessId}/${this.study.study_id}/${this.study.tasks[i].taskID}/${default_measurment_id[this.study.tasks[i].measurementOptions[i]]}/${this.study.factors[i].factorID}`
          //     axios
          //       .post(path, formData, {
          //         headers: {
          //           'Content-Type': 'multipart/form-data',
          //         },
          //       })
          //   }
          // }

          //********* WORK IN PROGRESS ******************************//
        }
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
      }
    },

    async startSession() {
      try {
        const path = 'http://127.0.0.1:5001/run_study'
        const response = await axios.post(path, this.study)
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
      }
    },
    getFileBlob_mouse(filePath) {
      try {
        // Example: Convert file content to Blob (assuming CSV data is to be fetched/generated)
        const csvContent = `data:text/csv;charset=utf-8,Time,running_time,x,y`

        return new Blob([csvContent], { type: 'text/csv' })
      } catch (error) {
        console.error('Error creating Blob:', error)
        return null
      }
    },
    getFileBlob_keyboard(filePath) {
      try {
        // Example: Convert file content to Blob (assuming CSV data is to be fetched/generated)
        const csvContent = `data:text/csv;charset=utf-8,Time,running_time,keys`

        return new Blob([csvContent], { type: 'text/csv' })
      } catch (error) {
        console.error('Error creating Blob:', error)
        return null
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
.cancel-begin-btn {
  min-height: 40px;
  min-width: 200px;
}
.v-progress-circular {
  margin: 1rem;
}
.timer-counter {
  width: 100%;
  height: 100vh;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}
.timer-msgs {
  text-align: center;
  margin-top: 1rem;
}
.timer-msg {
  font-size: 1.5rem;
  color: #555;
}
.timer-mini-msg {
  font-size: 1rem;
  color: #777;
  margin-top: 0.5rem;
}
.res-btn {
  min-height: 40px;
  min-width: 200px;
  margin-top: 10px;
}
</style>
