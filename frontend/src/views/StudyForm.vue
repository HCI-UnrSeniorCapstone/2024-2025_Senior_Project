<template>
  <v-container fluid>
    <!-- Page Title -->
    <v-row class="mt-4 mb-6" justify="center">
      <v-col cols="12" md="8">
        <v-card class="page-title-card pa-6 d-flex flex-column align-center">
          <h2 class="page-title">
            {{ editMode ? 'Edit Study' : 'Create New Study' }}
          </h2>
          <div class="page-subtitle mt-2">
            {{
              editMode
                ? 'Update your study details below'
                : 'Fill out the information to create your new study'
            }}
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-divider class="my-6" />

    <v-row justify="center">
      <v-col cols="12" md="10">
        <form @submit.prevent="submit">
          <!-- Study Details -->
          <h3 class="section-title mb-2">Study Details</h3>
          <v-card class="pa-4 mb-6 full-width-table">
            <StudyDetails
              v-model:studyName="studyName"
              v-model:studyDescription="studyDescription"
              v-model:studyDesignType="studyDesignType"
              v-model:participantCount="participantCount"
              :studyNameRules="studyNameRules"
              :studyDescriptionRules="studyDescriptionRules"
              :studyDesignTypeRules="studyDesignTypeRules"
              :participantCountRules="participantCountRules"
            />
          </v-card>

          <!-- Tasks -->
          <h3 class="section-title mb-2">Tasks</h3>
          <v-expansion-panels multiple v-model="expandedTPanels" class="mb-4">
            <v-expansion-panel v-for="(task, index) in tasks" :key="index">
              <v-expansion-panel-title @click="toggleTaskPanel(index)">
                <div class="d-flex justify-space-between align-center w-100">
                  <span>Task {{ index + 1 }}</span>
                </div>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <Task
                  :ref="el => (taskRefs[index] = el)"
                  :task="task"
                  @update:task="updateTask(index, $event)"
                />
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

          <div class="d-flex justify-end mb-6">
            <v-btn
              @click="addTaskFactor('task')"
              color="grey"
              class="add-rmv-btn"
              >+</v-btn
            >
            <v-btn
              @click="
                displayDialog({
                  title: 'Remove Task',
                  text: 'Are you sure you want to remove the last task?',
                  source: 'task',
                })
              "
              :disabled="!canRemoveTask"
              color="grey"
              class="add-rmv-btn"
              >-</v-btn
            >
          </div>

          <!-- Factors -->
          <h3 class="section-title mb-2">Factors</h3>
          <v-expansion-panels multiple v-model="expandedFPanels" class="mb-4">
            <v-expansion-panel v-for="(factor, index) in factors" :key="index">
              <v-expansion-panel-title @click="toggleFactorPanel(index)">
                <div class="d-flex justify-space-between align-center w-100">
                  <span>Factor {{ String.fromCharCode(65 + index) }}</span>
                </div>
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <Factor
                  :ref="el => (factorRefs[index] = el)"
                  :factor="factor"
                />
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

          <div class="d-flex justify-end mb-6">
            <v-btn
              @click="addTaskFactor('factor')"
              color="grey"
              class="add-rmv-btn"
              >+</v-btn
            >
            <v-btn
              @click="
                displayDialog({
                  title: 'Remove Factor',
                  text: 'Are you sure you want to remove the last factor?',
                  source: 'factor',
                })
              "
              :disabled="!canRemoveFactor"
              color="grey"
              class="add-rmv-btn"
              >-</v-btn
            >
          </div>

          <!-- Forms / Uploads -->
          <h3 class="section-title mb-2">Forms / Uploads</h3>
          <div class="text-medium-emphasis mb-2">
            (All uploads are optional)
          </div>

          <v-card class="pa-4 mb-6 full-width-table">
            <ConsentUpload
              v-model:consentUpload="consentUpload"
              v-model:showConsentPreview="showConsentPreview"
            />
            <SurveyUploads
              v-model:preSurveyUpload="preSurveyUpload"
              v-model:postSurveyUpload="postSurveyUpload"
              @update:parsedPreSurveyJson="parsedPreSurveyJson = $event"
              @update:parsedPostSurveyJson="parsedPostSurveyJson = $event"
              @update:surveyValidationError="surveyValidationError = $event"
              @update:surveyValidationErrorMsg="
                surveyValidationErrorMsg = $event
              "
            />
          </v-card>

          <v-btn
            variant="text"
            color="primary"
            prepend-icon="mdi-download"
            href="/sample_survey.json"
            download
            class="mb-8"
          >
            Download Template Questionnaire
          </v-btn>

          <!-- Save & Exit Buttons -->
          <v-row justify="center" class="my-6">
            <v-btn
              class="save-exit-btn me-4"
              @click="
                displayDialog({
                  title: 'Exit Confirmation',
                  text: 'Exit without saving?',
                  source: 'exit',
                })
              "
            >
              Exit
            </v-btn>
            <v-btn class="save-exit-btn" type="submit" :disabled="!isFormValid">
              Save
            </v-btn>
          </v-row>
        </form>
      </v-col>
    </v-row>

    <!-- Dialog -->
    <v-dialog v-model="dialog" max-width="400" persistent>
      <v-card
        prepend-icon="mdi-alert-outline"
        :title="dialogDetails.title"
        :text="dialogDetails.text"
      >
        <template v-slot:actions>
          <v-spacer />
          <v-btn @click="closeDialog()">Cancel</v-btn>
          <v-btn @click="closeDialog(dialogDetails.source)">Agree</v-btn>
        </template>
      </v-card>
    </v-dialog>

    <!-- Top Alert -->
    <v-alert v-if="saveStatus" :type="alertType" class="top-alert" closable>
      {{ alertMessage }}
    </v-alert>

    <!-- Error Snackbars -->
    <v-snackbar v-model="collapseError" :timeout="2000" color="red">
      {{ collapseErrorMsg }}
    </v-snackbar>

    <v-snackbar v-model="surveyValidationError" :timeout="5000" color="red">
      {{ surveyValidationErrorMsg }}
    </v-snackbar>
  </v-container>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/axiosInstance'

import Task from '../components/Task.vue'
import Factor from '../components/Factor.vue'
import StudyDetails from '@/components/StudyDetails.vue'
import ConsentUpload from '@/components/ConsentUpload.vue'
import SurveyUploads from '@/components/SurveyUploads.vue'
import { useStudyStore } from '@/stores/study'

export default {
  components: {
    Task,
    Factor,
    StudyDetails,
    ConsentUpload,
    SurveyUploads,
  },

  setup() {
    const router = useRouter()
    const exit = () => router.push({ name: 'UserStudies' })

    return {
      exit,
      taskRefs: ref([]),
      factorRefs: ref([]),
    }
  },

  data() {
    return {
      studyName: '',
      studyDescription: '',
      studyDesignType: null,
      participantCount: '',
      tasks: [],
      factors: [],
      expandedTPanels: [0],
      expandedFPanels: [0],

      // FILE UPLOADS
      //Consent
      consentUpload: null,
      showConsentPreview: false,
      //Pre-survey
      preSurveyUpload: null,
      parsedPreSurveyJson: null,
      preSurveyUploadValid: false,
      showPreSurveyPreview: false,
      // Post-survey
      postSurveyUpload: null,
      parsedPostSurveyJson: null,
      postSurveyUploadValid: false,
      showPostSurveyPreview: false,
      // Both surveys
      surveyValidationError: false,
      surveyValidationErrorMsg: '',

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
      dialog: false,
      dialogDetails: { title: '', text: '', source: '' },
      collapseError: false,
      collapseErrorMsg: 'Cannot collapse with improperly filled field(s)',
      saveStatus: false,
      alertType: 'success',
      alertMessage: '',
      studyID: null,
      userID: null,
      editMode: false,
    }
  },

  computed: {
    isFormValid() {
      const validate = (rules, value) =>
        rules.every(rule => rule(value) === true)

      const tasksValid = this.expandedTPanels.every(
        index => this.taskRefs[index]?.validateTaskFields?.() ?? true,
      )
      const factorsValid = this.expandedFPanels.every(
        index => this.factorRefs[index]?.validateFactorFields?.() ?? true,
      )

      return (
        validate(this.studyNameRules, this.studyName) &&
        validate(this.studyDescriptionRules, this.studyDescription) &&
        validate(this.studyDesignTypeRules, this.studyDesignType) &&
        validate(this.participantCountRules, this.participantCount) &&
        tasksValid &&
        factorsValid
      )
    },
    canRemoveTask() {
      return this.tasks.length > 1
    },
    canRemoveFactor() {
      return this.factors.length > 1
    },
  },

  mounted() {
    const studyStore = useStudyStore()
    this.studyID = studyStore.currentStudyID
    this.editMode = !!this.studyID

    if (this.editMode) {
      this.fetchStudyDetails(this.studyID)
    } else {
      // Clean out leftover edit fields
      this.studyName = ''
      this.studyDescription = ''
      this.studyDesignType = null
      this.participantCount = ''
      this.tasks = []
      this.factors = []
      this.addTaskFactor('task')
      this.addTaskFactor('factor')
    }
  },

  methods: {
    async convertFileToBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => {
          const base64String = reader.result.split(',')[1] // Strip the data prefix
          resolve({
            filename: file.name,
            content: base64String,
          })
        }
        reader.onerror = reject
        reader.readAsDataURL(file)
      })
    },
    addTaskFactor(type) {
      const isTask = type === 'task'
      const list = isTask ? this.tasks : this.factors
      const panels = isTask ? this.expandedTPanels : this.expandedFPanels

      list.push(
        isTask
          ? {
              taskName: '',
              taskDescription: '',
              taskDirections: '',
              taskDuration: '',
              measurementOptions: [],
            }
          : { factorName: '', factorDescription: '' },
      )
      panels.push(list.length - 1)
    },

    removeTaskFactor(type) {
      const list = type === 'task' ? this.tasks : this.factors
      const panels =
        type === 'task' ? this.expandedTPanels : this.expandedFPanels
      const lastIndex = list.length - 1

      list.pop()
      panels.splice(panels.indexOf(lastIndex), 1)
    },

    updateTask(index, updatedTask) {
      this.tasks[index] = { ...updatedTask }
    },

    toggleTaskPanel(index) {
      const taskRef = this.taskRefs[index]
      if (!taskRef?.validateTaskFields?.()) {
        if (!this.expandedTPanels.includes(index)) {
          this.expandedTPanels.push(index)
          this.collapseError = true
        }
      } else {
        this.expandedTPanels = this.expandedTPanels.filter(i => i !== index)
      }
    },

    toggleFactorPanel(index) {
      const factorRef = this.factorRefs[index]
      if (!factorRef?.validateFactorFields?.()) {
        if (!this.expandedFPanels.includes(index)) {
          this.expandedFPanels.push(index)
          this.collapseError = true
        }
      } else {
        this.expandedFPanels = this.expandedFPanels.filter(i => i !== index)
      }
    },

    displayDialog(details) {
      this.dialogDetails = details
      this.dialog = true
    },

    closeDialog(action) {
      if (action === 'task' || action === 'factor') {
        this.removeTaskFactor(action)
      } else if (action === 'exit') {
        this.exit()
      }
      this.dialog = false
    },

    studySaveStatus(type, msg) {
      this.alertType = type
      this.alertMessage = msg
      this.saveStatus = true
      setTimeout(() => (this.saveStatus = false), 1500)
    },

    // Retrieve study details if we are editing an existing study
    async fetchStudyDetails(studyID) {
      try {
        const response = await api.post(
          `/load_study`,
          { studyID },
          { headers: { 'Content-Type': 'application/json' } },
        )
        const study = response.data

        Object.assign(this, {
          studyName: study.studyName,
          studyDescription: study.studyDescription,
          studyDesignType: study.studyDesignType,
          participantCount: study.participantCount,
          tasks: study.tasks.map(t => ({
            ...t,
            taskDuration: t.taskDuration !== null ? t.taskDuration : '',
          })),
          factors: study.factors,
        })

        // Consent form
        await this.fetchConsentForm(studyID)
        //Pre Survey form
        await this.fetchSurveyForm(studyID, 'pre')
        //Post Survey form
        await this.fetchSurveyForm(studyID, 'post')
      } catch (error) {
        console.error('Failed to fetch study details:', error)
      }
    },

    async fetchConsentForm(studyID) {
      try {
        const consentResponse = await api.post(
          '/get_study_consent_form',
          { study_id: studyID },
          { responseType: 'blob' },
        )
        if (consentResponse.status === 200) {
          const fileName =
            consentResponse.headers['x-original-filename'] || 'consent_form.pdf'
          this.consentUpload = new File([consentResponse.data], fileName, {
            type: 'application/pdf',
          })
        }
      } catch (err) {
        if (err.response.status !== 204) {
          console.warn('Consent form retrieval failed:', err)
        }
      }
    },

    async fetchSurveyForm(studyID, type) {
      try {
        const response = await api.post(
          '/get_study_survey_form',
          { study_id: studyID, survey_type: type },
          { responseType: 'blob' },
        )
        if (response.status === 200) {
          const fileName =
            response.headers['x-original-filename'] ||
            `${type}_survey_questionnaire.json`
          const file = new File([response.data], fileName, {
            type: 'application/json',
          })
          this[`${type}SurveyUpload`] = file
        }
      } catch (err) {
        if (err.response.status !== 204) {
          console.warn(`${type} survey form retrieval failed:`, err)
        }
      }
    },

    async submit() {
      const payload = {
        studyName: this.studyName,
        studyDescription: this.studyDescription,
        studyDesignType: this.studyDesignType,
        participantCount: this.participantCount,
        tasks: this.tasks,
        factors: this.factors,
        studyID: this.studyID,
      }

      // Handle base64 encoding of all forms currently uploaded
      if (this.consentUpload) {
        payload.consentFile = await this.convertFileToBase64(this.consentUpload)
      }
      if (this.preSurveyUpload) {
        payload.preSurveyFile = await this.convertFileToBase64(
          this.preSurveyUpload,
        )
      }
      if (this.postSurveyUpload) {
        payload.postSurveyFile = await this.convertFileToBase64(
          this.postSurveyUpload,
        )
      }

      try {
        const path = this.editMode ? `/overwrite_study` : `/create_study`

        const res = await api.post(path, payload)

        this.studySaveStatus('success', 'Study saved successfully!')
        setTimeout(() => this.exit(), 1500)
      } catch (error) {
        console.error('Submit error:', error.response?.data || error.message)
        this.studySaveStatus('error', 'Study failed to save!')
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
.top-alert {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 2000;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}
.page-title {
  font-size: 28px;
  font-weight: 700;
}

.section-title {
  font-size: 22px;
  font-weight: 600;
  color: #333;
}

.full-width-table {
  background-color: #ffffff !important;
  border-radius: 12px;
  overflow: hidden;
}

.save-exit-btn {
  font-size: 16px;
  font-weight: bold;
  padding: 10px 20px;
  text-transform: none;
  min-height: 40px;
  min-width: 125px;
}

.add-rmv-btn {
  max-height: 32px;
  min-width: 32px;
  font-size: larger;
}
.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #222;
  margin-bottom: 4px; /* nice breathing between title and subtitle */
}

.page-subtitle {
  font-size: 18px;
  font-weight: 400;
  color: #666;
}
.page-title-card {
  background: linear-gradient(to right, #fefefe, #f8f8f8);
  border-radius: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #222;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 18px;
  font-weight: 400;
  color: #666;
}
</style>
