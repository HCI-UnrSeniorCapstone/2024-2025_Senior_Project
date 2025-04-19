<template>
  <v-main>
    <v-row>
      <v-col cols="12" md="10" offset-md="1">
        <v-progress-linear
          :model-value="progressTracker"
          height="10"
          color="primary"
          class="mb-6"
          striped
        />
      </v-col>
    </v-row>
    <v-container class="mt-5">
      <v-row>
        <v-col cols="12" md="10" offset-md="1">
          <!-- Consent Ack (if applicable) -->
          <ConsentAckScreen
            v-if="currStepIndex == 0"
            :display="showConsentForm"
            @update:display="$emit('update:showConsentForm', $event)"
            :form="consentForm"
            :participantSessId="participantSessId"
            :studyId="sessionJson?.study_id"
            :liveSession="true"
            @submit="handleConsentAck"
          />

          <!-- Demographic Form (always) -->
          <DemographicForm
            v-if="currStepIndex == 1"
            :studyId="sessionJson?.study_id"
            @submit="handleDemographicSubmit"
          />

          <!-- Pre-survey Form (if applicable) -->
          <SessionSurvey
            v-if="showPreSurveyForm && currStepIndex == 2"
            :surveyJson="preSurveyForm"
            :participantSessId="participantSessId"
            survey_type="pre"
            @submit="advanceNextStep"
          />

          <!-- Session Launcher (always) -->
          <SessionLaunch
            v-if="currStepIndex == 3"
            :startCountdown="true"
            :duration="15"
            description="About to begin experiment"
            @submit="advanceNextStep"
          />

          <!-- Post-survey Form (if applicable) -->
          <SessionSurvey
            v-if="showPostSurveyForm && currStepIndex == 4"
            :surveyJson="postSurveyForm"
            :participantSessId="participantSessId"
            survey_type="post"
            @submit="advanceNextStep"
          />

          <!-- Researcher Notes/Comments (always) -->
          <ResearcherNotes
            v-if="currStepIndex == 5"
            :participantSessId="participantSessId"
            @submit="exit"
          />
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script>
import api from '@/axiosInstance'
import { useRouter } from 'vue-router'
import ConsentAckScreen from '@/components/ConsentAckScreen.vue'
import DemographicForm from '@/components/DemographicForm.vue'
import SessionSurvey from '@/components/SessionSurvey.vue'
import SessionLaunch from '@/components/SessionLaunch.vue'
import ResearcherNotes from '@/components/ResearcherNotes.vue'
import { useStudyStore } from '@/stores/study'

export default {
  components: {
    ConsentAckScreen,
    DemographicForm,
    SessionSurvey,
    SessionLaunch,
    ResearcherNotes,
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
      currStepIndex: 0,
      participantSessId: null,
      sessionJson: null,
      // Consent vars
      consentForm: null,
      hasConsentForm: false,
      showConsentForm: false,
      consentReceived: false,
      // Pre survey vars
      preSurveyForm: null,
      hasPreSurveyForm: false,
      showPreSurveyForm: false,
      // Post survey vars
      postSurveyForm: null,
      hasPostSurveyForm: false,
      showPostSurveyForm: false,
    }
  },

  async mounted() {
    this.sessionJson = useStudyStore().sessionJson
    console.log('Session JSON Runner:', this.sessionJson)

    if (this.sessionJson?.study_id) {
      this.fetchForms()
    } else {
      console.warn('No session data available. Redirecting...')
      this.$router.push({ name: 'UserStudies' })
    }
  },

  computed: {
    progressTracker() {
      return ((this.currStepIndex + 1) / 6) * 100
    },
  },

  methods: {
    advanceNextStep() {
      this.currStepIndex++

      // Skip steps where no pre/post/consent forms provided for the flow
      while (
        (this.currStepIndex === 0 && !this.hasConsentForm) ||
        (this.currStepIndex === 2 && !this.hasPreSurveyForm) ||
        (this.currStepIndex === 4 && !this.hasPostSurveyForm)
      ) {
        this.currStepIndex++
      }
    },
    async handleDemographicSubmit(sessionId) {
      this.participantSessId = sessionId
      if (this.hasConsentForm) {
        await this.saveConsentAck()
      }
      this.advanceNextStep() // move to pre-survey (possibly)
    },
    handleConsentAck() {
      this.consentReceived = true
      this.advanceNextStep() // move to demographic form (always)
    },
    async saveConsentAck() {
      if (
        !this.participantSessId ||
        !this.sessionJson?.study_id ||
        !this.consentReceived
      ) {
        return
      }
      try {
        const path = `/save_participant_consent`
        await api.post(path, {
          study_id: this.sessionJson?.study_id,
          participant_session_id: this.participantSessId,
        })
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
        return
      }
    },
    async fetchConsentForm() {
      try {
        const path = `/get_study_consent_form`
        const response = await api.post(
          path,
          { study_id: this.sessionJson.study_id },
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
          this.showConsentForm = false
        }
      } catch (err) {
        // Expected a consent form but failed to get it so still show ack dialog even if they cannot see the form
        console.warn('Error fetching consent form:', err)
        this.consentForm = null
        this.hasConsentForm = true // Supposed to but did not populate, but we can still get ack
        this.showConsentForm = true
      }
    },
    async fetchSurveyForm(survey_type) {
      try {
        const response = await api.post(
          '/get_study_survey_form',
          { study_id: this.sessionJson.study_id, survey_type: survey_type },
          { responseType: 'blob' },
        )
        if (response.status === 200) {
          const fileName =
            response.headers['x-original-filename'] ||
            `${survey_type}_survey_questionnaire.json`
          const file = new File([response.data], fileName, {
            type: 'application/json',
          })
          const text = await file.text()
          this[`${survey_type}SurveyForm`] = JSON.parse(text)

          if (survey_type == 'pre') {
            this.hasPreSurveyForm = true
            this.showPreSurveyForm = true
          } else if (survey_type == 'post') {
            this.hasPostSurveyForm = true
            this.showPostSurveyForm = true
          }
        } else if (response.status === 204) {
          if (survey_type == 'pre') {
            this.hasPreSurveyForm = false
            this.showPreSurveyForm = false
          } else if (survey_type == 'post') {
            this.hasPostSurveyForm = false
            this.showPostSurveyForm = false
          }
        }
      } catch (err) {
        if (err.response.status !== 204) {
          console.warn(`${survey_type} survey form retrieval failed:`, err)
        }
      }
    },
    async fetchForms() {
      await this.fetchConsentForm()
      await this.fetchSurveyForm('pre')
      await this.fetchSurveyForm('post')

      if (this.currStepIndex === 0 && !this.hasConsentForm) {
        this.advanceNextStep()
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
.quit-btn {
  min-height: 40px;
  min-width: 200px;
}
</style>
