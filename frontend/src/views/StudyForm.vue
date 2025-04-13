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
                  <Task
                    :ref="el => (taskRefs[index] = el)"
                    :task="tasks[index]"
                    @update:task="updateTask(index, $event)"
                  />
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

            <h3>Forms/Uploads</h3>
            <div class="text-medium-emphasis">
              (All file uploads below are optional)
            </div>
            <!-- Consent Form Upload -->
            <FileUploadAndPreview
              v-model="consentUpload"
              label="Consent Form (PDF)"
              accept=".pdf,.txt,.md"
              :preview-disabled="!consentUpload"
              @preview="previewConsentForm"
            ></FileUploadAndPreview>

            <ConsentAckScreen
              v-model:display="showConsentPreview"
              :form="consentUpload"
            />

            <!-- Provide a template Survey to help -->
            <v-btn
              class="mt-8"
              variant="text"
              color="primary"
              prepend-icon="mdi-download"
              href="/sample_survey.json"
              download
            >
              Download Template Questionnaire
            </v-btn>

            <!-- Pre-survey Questions Upload -->
            <FileUploadAndPreview
              v-model="preSurveyUpload"
              label="Pre-survey Questionnaire (JSON)"
              accept=".json"
              :preview-disabled="!preSurveyUploadValid"
              @preview="showPreSurveyPreview = true"
            ></FileUploadAndPreview>

            <!-- Pre-survey Questions Preview Dialog -->
            <v-dialog v-model="showPreSurveyPreview" class="survey-dialog">
              <v-card title="Pre-survey Questionnaire Preview">
                <v-card-text>
                  <Questionnaire
                    :surveyJson="parsedPreSurveyJson"
                    :readOnly="false"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-btn
                    text="Close"
                    @click="showPreSurveyPreview = false"
                  ></v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <!-- Post-survey Questions Upload -->
            <FileUploadAndPreview
              v-model="postSurveyUpload"
              label="Post-survey Questionnaire (JSON)"
              accept=".json"
              :preview-disabled="!postSurveyUploadValid"
              @preview="showPostSurveyPreview = true"
            ></FileUploadAndPreview>

            <!-- Post-survey Questions Preview Dialog -->
            <v-dialog v-model="showPostSurveyPreview" class="survey-dialog">
              <v-card title="Post-survey Questionnaire Preview">
                <v-card-text>
                  <Questionnaire
                    :surveyJson="parsedPostSurveyJson"
                    :readOnly="false"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-btn
                    text="Close"
                    @click="showPostSurveyPreview = false"
                  ></v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-row class="btn-row mt-8" justify="center">
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

    <div>
      <v-alert v-if="saveStatus" :type="alertType" class="top-alert" closable>
        {{ alertMessage }}
      </v-alert>
    </div>
  </v-main>

  <v-snackbar v-model="collapseError" :timeout="2000" color="red">
    {{ collapseErrorMsg }}
  </v-snackbar>

  <v-snackbar v-model="surveyValidationError" :timeout="5000" color="red">
    {{ surveyValidationErrorMsg }}
  </v-snackbar>
</template>

<script>
import Task from '../components/Task.vue'
import Factor from '../components/Factor.vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
import FileUploadAndPreview from '@/components/FileUploadAndPreview.vue'
import ConsentAckScreen from '@/components/ConsentAckScreen.vue'
import Questionnaire from '@/components/Questionnaire.vue'

export default {
  components: {
    Task,
    Factor,
    FileUploadAndPreview,
    ConsentAckScreen,
    Questionnaire,
  },

  setup() {
    const router = useRouter()
    const exit = () => {
      router.push({ name: 'UserStudies' })
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
      // study saved successfully
      saveStatus: false,
      alertType: 'success',
      alertMessage: '',
    }
  },

  // view will load with 1 task and factor populated automatically
  async mounted() {
    this.addTaskFactor('task')
    this.addTaskFactor('factor')
    // Passed params when an existing study is being opened for editing
    this.studyID = this.$route.params.studyID || null
    this.userID = this.$route.params.userID || null
    this.editMode = !!this.studyID

    if (this.editMode) {
      await this.fetchStudyDetails(this.studyID)
    }
  },

  watch: {
    // Start validation as soon as survey files are uploaded (pre/post)
    preSurveyUpload(newFile) {
      if (newFile) {
        this.validateSurveyUpload(newFile, 'pre')
      } else {
        this.preSurveyUploadValid = false
        this.parsedPreSurveyJson = null
      }
    },
    postSurveyUpload(newFile) {
      if (newFile) {
        this.validateSurveyUpload(newFile, 'post')
      }
      this.postSurveyUploadValid = false
      this.parsedPostSurveyJson = null
    },
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

    updateTask(index, updatedTask) {
      this.tasks[index] = { ...updatedTask }
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

    previewConsentForm() {
      if (this.consentUpload) {
        this.showConsentPreview = true
      }
    },

    studySaveStatus(type, msg) {
      this.alertType = type
      this.alertMessage = msg
      this.saveStatus = true
      setTimeout(() => {
        this.saveStatus = false
      }, 1500)
    },

    // Try to validate survey JSON uploads
    async validateSurveyUpload(surveyFile, type) {
      const formData = new FormData()
      formData.append('survey_file', surveyFile)

      try {
        const backendUrl = this.$backendUrl
        let path = `${backendUrl}/validate_survey_upload`
        const validatedJson = await axios.post(path, formData)

        if (type == 'pre') {
          this.preSurveyUploadValid = true
          this.parsedPreSurveyJson = validatedJson.data
        } else if (type == 'post') {
          this.postSurveyUploadValid = true
          this.parsedPostSurveyJson = validatedJson.data
        }
        this.surveyValidationError = false
        this.surveyValidationErrorMsg = ''
      } catch (err) {
        let error_msg = 'Error occured during survey validation'
        if (err.response?.data?.error_message) {
          const data = err.response.data
          error_msg = `${data.error_type}: ${data.error_message}`

          if (data.location?.length) {
            error_msg += ` at ${data.location.join('.')}`
          }
        }
        this.surveyValidationErrorMsg = error_msg
        this.surveyValidationError = true

        // Reset values accordingly
        if (type == 'pre') {
          this.preSurveyUploadValid = false
          this.parsedPreSurveyJson = null
        } else if (type == 'post') {
          this.postSurveyUploadValid = false
          this.parsedPostSurveyJson = null
        }
      }
    },

    // Retrieve study details if we are editing an existing study
    async fetchStudyDetails(studyID) {
      try {
        const backendUrl = this.$backendUrl
        let path = `${backendUrl}/load_study/${studyID}`
        const response = await axios.get(path)

        const study_edit = response.data

        this.studyName = study_edit.studyName
        this.studyDescription = study_edit.studyDescription
        this.studyDesignType = study_edit.studyDesignType
        this.participantCount = study_edit.participantCount
        this.tasks = study_edit.tasks.map(task => ({
          ...task,
          taskDuration: task.taskDuration !== null ? task.taskDuration : '',
        }))
        this.factors = study_edit.factors

        // Consent form
        try {
          path = `${backendUrl}/get_study_consent_form/${studyID}`
          const consentResponse = await axios.get(path, {
            responseType: 'blob',
          })
          if (consentResponse.status == 200) {
            const fName =
              consentResponse.headers['x-original-filename'] ||
              'consent_form.pdf'
            const blob = new File([consentResponse.data], fName, {
              type: 'application/pdf',
            })
            this.consentUpload = blob
          }
        } catch (err) {
          if (err.response.status !== 204) {
            console.warn('Consent form retrieval failed:', err)
          }
        }
      } catch (error) {
        console.error('Error fetching details of existing study:', error)
      }
    },

    async submit() {
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

      try {
        const backendUrl = this.$backendUrl
        let path
        const formData = new FormData()

        formData.append('data', JSON.stringify(submissionData))
        if (this.consentUpload) {
          formData.append('consent_file', this.consentUpload)
        }

        let response
        // Editing existing study > overwrite
        if (this.studyID && this.userID) {
          path = `${backendUrl}/overwrite_study/${this.userID}/${this.studyID}`
          response = await axios.post(path, formData)
        } else {
          // Creating a new study
          path = `${backendUrl}/create_study/1`
          response = await axios.post(path, formData)
        }

        // Everything successfully saved
        this.studySaveStatus('success', 'Study saved successfully!')
        setTimeout(() => {
          this.exit()
        }, 1500)
      } catch (error) {
        this.studySaveStatus('error', 'Study failed to save!')
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
.survey-dialog {
  width: 60vw;
  max-width: 1500px;
  max-height: none;
}
</style>
