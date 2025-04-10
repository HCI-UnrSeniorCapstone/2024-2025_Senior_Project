<template>
  <v-main>
    <v-container class="mt-5">
      <ConsentAckScreen
        v-model:display="showConsentForm"
        :form="consentForm"
        @acknowledged="onAcknowledgement"
      />
      <v-row v-if="showDemographicForm">
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
                class="me-4 quit-next-btn"
                color="error"
                @click="
                  displayDialog({
                    title: 'Quit Confirmation',
                    text: 'Are you sure you want to quit the session?',
                    source: 'quit',
                  })
                "
                >Quit</v-btn
              >
              <v-btn
                class="me-4 quit-next-btn"
                type="submit"
                :disabled="
                  !isFormValid ||
                  !showDemographicForm ||
                  (hasConsentForm && !consentAcknowledged)
                "
                @click="
                  displayDialog({
                    title: 'Continue',
                    text: 'Are you sure you want to move forward?',
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
import ConsentAckScreen from '@/components/ConsentAckScreen.vue'

export default {
  props: ['formattedStudy'],

  components: {
    ConsentAckScreen,
  },

  setup() {
    const router = useRouter()
    const exit = () => {
      router.push({ name: 'UserStudies' })
    }

    return { exit }
  },

  data() {
    return {
      showDemographicForm: false,
      studyData: null,
      participantSessId: null,

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

      // Participant Consent Fields
      showConsentForm: false,
      consentForm: null,
      consentAcknowledged: false,
      hasConsentForm: false,
    }
  },

  mounted() {
    this.studyData = this.formattedStudy
  },

  watch: {
    formattedStudy: {
      handler(newVal) {
        if (newVal && newVal.study_id) {
          this.studyData = newVal
          this.fetchConsentForm()
        }
      },
      immediate: true,
    },
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
  },

  methods: {
    // dynamic confirmation for quitting or advancing the session
    displayDialog(details) {
      this.dialogDetails = details
      this.dialog = true
    },

    // if they agree to exit we route elsewhere, if they agree to start we notify they can close window and start session
    closeDialog(source) {
      if (source == 'next') {
        this.moveNext()
      } else if (source == 'quit') {
        this.exit()
      }
      this.dialog = false
    },

    async moveNext() {
      try {
        await this.getSessionID()
        if (this.participantSessId) {
          if (this.hasConsentForm && this.consentAcknowledged) {
            await this.saveParticipantAck()
          }

          // Add to study data to make complete pkg needed for session to run
          this.studyData.participantSessId = this.participantSessId

          // await this.startSession()
        } else {
          console.warn('Participant session id not generated')
        }
      } catch (error) {
        console.error('Error moving to next step:', error)
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
        const path = `/create_participant_session/${this.studyData.study_id}`
        const response = await api.post(path, submissionData)
        this.participantSessId = response.data.participant_session_id
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
      }
    },

    async fetchConsentForm() {
      try {
        const path = `/get_study_consent_form`
        const response = await api.post(
          path,
          { study_id: this.studyData.study_id },
          {
            responseType: 'blob',
          },
        )

        if (response.status === 200) {
          const fileName =
            response.headers['x-original-filename'] || 'consent_form.pdf'
          const blob = new File([response.data], fileName, {
            type: 'application/pdf',
          })
          this.consentForm = blob
          this.hasConsentForm = true
          this.showConsentForm = true
        } else if (response.status === 204) {
          this.hasConsentForm = false
          this.showDemographicForm = true
        }
      } catch (err) {
        // Expected a consent form but failed to get it so still show ack dialog even if they cannot see the form
        console.warn('Error fetching consent form:', err)
        this.consentForm = null
        this.hasConsentForm = true // Supposed to but did not populate, but we can still get ack
        this.showConsentForm = true
      }
    },

    onAcknowledgement() {
      this.consentAcknowledged = true
      this.showConsentForm = false
      this.showDemographicForm = true
    },

    async saveParticipantAck() {
      try {
        const path = `/save_participant_consent/${this.studyData.study_id}/${this.participantSessId}`
        await api.post(path)
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
      }
    },

    async startSession() {
      try {
        const path = 'http://127.0.0.1:5001/run_study'
        const response = await api.post(path, this.studyData)
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
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
.quit-next-btn {
  min-height: 40px;
  min-width: 200px;
}
</style>
