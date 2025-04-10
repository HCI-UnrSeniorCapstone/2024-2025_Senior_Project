<template>
  <v-navigation-drawer
    v-model="drawerProxy"
    location="right"
    temporary
    :width="1000"
  >
    <v-toolbar flat dense color="white">
      <v-toolbar-title> {{ studyName }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn v-tooltip="'Close'" icon @click="closeDrawer">
        <v-icon color="secondary">mdi-close</v-icon>
      </v-btn>
    </v-toolbar>

    <v-divider class="mb-2"></v-divider>

    <v-container class="py-2 px-4">
      <p class="study-description">{{ studyDescription }}</p>
    </v-container>

    <v-container>
      <v-tabs
        v-model="tab"
        background-color="transparent"
        grow
        class="custom-tabs"
      >
        <v-tab>Overview</v-tab>
        <v-tab>Tasks</v-tab>
        <v-tab>Factors</v-tab>
      </v-tabs>

      <v-divider></v-divider>

      <v-card-text>
        <v-tabs-window v-model="tab">
          <v-tabs-window-item value="one">
            <v-row>
              <v-col>
                <v-card class="metric-card">
                  <v-icon color="primary">mdi-account-group</v-icon>
                  {{ participantCount + ' expected participants' }}
                </v-card>
                <v-divider class="mb-2"></v-divider>
                <v-card class="metric-card">
                  <v-icon color="primary">mdi-swap-horizontal</v-icon>
                  {{ studyDesignType + ' (study design type)' }}
                </v-card>
                <v-divider class="mb-2"></v-divider>
                <v-card class="metric-card">
                  <v-icon color="primary">mdi-format-list-checks</v-icon>
                  {{ tasks.length + ' tasks' }}
                </v-card>
                <v-divider class="mb-2"></v-divider>
                <v-card class="metric-card">
                  <v-icon color="primary">mdi-vector-combine</v-icon>
                  {{ factors.length + ' factors' }}
                </v-card>
                <v-divider class="mb-2"></v-divider>
              </v-col>
            </v-row>
          </v-tabs-window-item>

          <v-tabs-window-item value="two">
            <h4>Tasks</h4>
            <v-list>
              <v-list-item v-for="(task, index) in tasks" :key="index">
                <v-list-item-title>{{ task.taskName }}</v-list-item-title>
                <v-list-item-subtitle>{{
                  task.taskDescription || 'No task description provided'
                }}</v-list-item-subtitle>
                <p class="task-detail">
                  Duration:
                  {{
                    task.taskDuration && !isNaN(task.taskDuration)
                      ? parseFloat(task.taskDuration).toFixed(2) + ' minutes'
                      : 'No duration set'
                  }}
                </p>
                <p class="task-detail">
                  Measurements Selected:
                  <template v-if="task.measurementOptions.length > 0">
                    <v-chip
                      size="xsmall"
                      variant="tonal"
                      color="primary"
                      rounded
                      v-for="(option, i) in task.measurementOptions"
                      :key="i"
                    >
                      {{ option }}
                    </v-chip>
                  </template>
                  <span v-else>N/A</span>
                </p>
                <v-divider class="mb-2"></v-divider>
              </v-list-item>
            </v-list>
          </v-tabs-window-item>

          <v-tabs-window-item value="three">
            <h4>Factors</h4>
            <v-list>
              <v-list-item v-for="(factor, index) in factors" :key="index">
                <v-list-item-title>{{ factor.factorName }}</v-list-item-title>
                <v-list-item-subtitle>{{
                  factor.factorDescription || 'No factor description provided'
                }}</v-list-item-subtitle>
                <v-divider class="mb-2"></v-divider>
              </v-list-item>
            </v-list>
          </v-tabs-window-item>
        </v-tabs-window>
      </v-card-text>
    </v-container>

    <v-container>
      <v-row class="mb-3">
        <v-col cols="12">
          <h4>Sessions</h4>
          <v-card flat>
            <v-data-table
              :headers="headers"
              :items="sessions"
              dense
              class="elevation-2"
            >
              <template v-slot:item.sessionName="{ item }">
                <div class="study-name">
                  {{ item.sessionName }}
                </div>
              </template>
              <template v-slot:item.status="{ value }">
                <v-chip :color="getColor(value)" dark>
                  {{ value }}
                </v-chip>
              </template>
              <template v-slot:item.comment="{ item }">
                <div>
                  {{
                    item.comment.length > 100
                      ? item.comment.substring(0, 100) + '...'
                      : item.comment
                  }}
                </div>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-icon
                  v-tooltip="'Download Results'"
                  class="me-2"
                  size="small"
                  @click.stop="downloadParticipantSessionData(item.sessionID)"
                >
                  mdi-download
                </v-icon>
                <v-icon
                  v-tooltip="'Open'"
                  class="me-2"
                  size="small"
                  @click.stop="openSession(item)"
                >
                  mdi-arrow-expand
                </v-icon>
                <v-icon v-tooltip="'Delete'" size="small"> mdi-delete </v-icon>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <v-container class="d-flex flex-column align-center">
      <!-- <h4>Trial Coverage</h4> -->
      <v-card flat style="width: 80%; margin-left: 6%">
        <coverage-heatmap
          :tasks="heatmapTasks"
          :factors="heatmapFactors"
          :trials="heatmapMatrix"
          :chart-height="200"
        />
      </v-card>
    </v-container>

    <v-row justify="center">
      <v-col cols="auto">
        <v-btn @click="startNewSession" color="red">Start New Session</v-btn>
      </v-col>
    </v-row>
  </v-navigation-drawer>
</template>

<script>
import api from '@/axiosInstance'
import CoverageHeatmap from '@/components/CoverageHeatmap.vue'

export default {
  props: {
    drawer: {
      type: Boolean,
      required: true,
    },
    studyID: {
      type: Number,
      required: true,
    },
  },
  components: {
    CoverageHeatmap,
  },
  data() {
    return {
      studyName: '',
      studyDescription: '',
      studyDesignType: '',
      participantCount: '',
      tasks: [],
      factors: [],
      tab: null,
      focus_study: '',
      // For the sessions table
      headers: [
        {
          align: 'start',
          key: 'dateConducted',
          sortable: false,
          title: 'Date Conducted',
        },
        { key: 'sessionName', title: 'Session Name', sortable: false },
        { key: 'status', title: 'Status', sortable: false },
        { key: 'comment', title: 'Comments', sortable: false },
        { key: 'actions', title: 'Actions', sortable: false },
      ],
      // Holds all the sessions returned from the db query
      sessions: [],
      // Heatmap details
      heatmapMatrix: {},
      heatmapTasks: [],
      heatmapFactors: [],
    }
  },

  computed: {
    drawerProxy: {
      get() {
        // For reading the parent's value (in UserStudies.vue)
        return this.drawer
      },
      set(value) {
        // Emits an update/notification to the parent
        this.$emit('update:drawer', value)
      },
    },
  },

  // Watching for dynamic changes to the studyID and calls fetch route when it changes
  watch: {
    studyID: {
      immediate: true,
      handler(newStudyID) {
        if (newStudyID) {
          this.fetchStudyDetails(newStudyID)
          this.populateSessions(newStudyID)
        } else {
          console.warn('studyID not defined on mount')
        }
      },
    },
  },

  async mounted() {
    // For populating trial coverage heatmap immediately
    this.getTrialOccurrences()
  },

  methods: {
    // Retrieving all information on the study
    async fetchStudyDetails(studyID) {
      if (!studyID) {
        console.warn('No studyID to use as needed by the route')
        return
      }
      try {
        const response = await api.post('/load_study', { studyID })
        this.focus_study = response.data

        this.focus_study = response.data

        console.log(this.focus_study)

        this.studyName = this.focus_study.studyName
        this.studyDescription =
          this.focus_study.studyDescription || 'No study description'
        this.studyDesignType = this.focus_study.studyDesignType
        this.participantCount = this.focus_study.participantCount
        this.tasks = this.focus_study.tasks
        this.factors = this.focus_study.factors
      } catch (error) {
        console.error('Error fetching study details:', error)
      }
    },

    // Download a zip with the data of all sessions under the given study
    async downloadParticipantSessionData(sessionID) {
      try {
        const path = `/get_all_session_data_instance_from_participant_session_zip/${sessionID}`

        const response = await api.get(path, {
          responseType: 'blob',
        })
        // Get the content-disposition header to extract the filename
        const disposition = response.headers['content-disposition']
        const filename = disposition
          ? disposition.split('filename=')[1].replace(/"/g, '') // Extracting the filename from header
          : 'download.zip'

        // Download
        const blob = new Blob([response.data], { type: 'application/zip' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = filename
        link.click()
      } catch (error) {
        console.error('Error downloading session data:', error)
      }
    },

    // Populating the sessions table
    async populateSessions(sessionID) {
      try {
        const path = `/get_all_session_info/${sessionID}`
        const response = await api.get(path)

        console.log(response)
        if (Array.isArray(response.data)) {
          this.sessions = response.data.map(session => ({
            sessionID: session[0],
            sessionName: `Session ${session[1]}`,
            dateConducted: session[2],
            status: session[3],
            comment: session[4],
          }))
        }
      } catch (error) {
        console.error('Error retrieving sessions: ', error)
      }
    },

    // Getting trial appearances from prior sessions to populate the heatmap
    async getTrialOccurrences() {
      try {
        const path = `/get_trial_occurrences/${this.studyID}`
        const response = await api.get(path)

        this.heatmapTasks = this.tasks.map(t => t.taskName)
        this.heatmapFactors = this.factors.map(f => f.factorName)
        this.heatmapMatrix = response.data.matrix
      } catch (error) {
        console.error('Error fetching trial occurrences:', error)
      }
    },

    closeDrawer() {
      this.$emit('update:drawer', false)
    },

    // Routes to session reporting pg if user selects a specific session to look at
    openSession(item) {
      this.$router.push({
        name: 'SessionReporting',
        params: { id: item.sessionID },
      })
    },

    // Determines the status color
    getColor(status) {
      if (status == 'Invalid') {
        return 'red'
      } else {
        return 'green'
      }
    },

    // Route to view for session setup
    startNewSession() {
      this.$router.push({ name: 'SessionSetup', params: { id: this.studyID } })
    },
  },
}
</script>

<style>
.study-name {
  font-weight: bold;
}
.v-toolbar-title {
  font-size: 18px;
}
.v-divider {
  margin: 10px 0;
}
.elevation-2 {
  background-color: #ffffff;
}
.v-chip {
  font-size: 14px;
  margin: 3px;
  padding: 2px 4px;
}
.custom-tabs {
  background: transparent !important;
  border-bottom: 1px solid #ccc;
}
.v-tab {
  color: #000;
}
.v-tab--active {
  font-weight: bold;
  border-bottom: 2px solid #3f51b5 !important;
  color: #3f51b5 !important;
}
.study-description {
  color: #595959;
  font-size: 14px;
  font-weight: 400;
  margin-bottom: 10px;
}
.task-detail {
  margin-left: 20px;
  font-size: 14px;
  color: #595959;
}
</style>
