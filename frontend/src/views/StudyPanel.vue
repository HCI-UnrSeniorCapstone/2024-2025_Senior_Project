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
      <v-btn icon @click="editStudy">
        <v-icon color="secondary">mdi-pencil</v-icon>
      </v-btn>
      <v-btn icon @click="closeDrawer">
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
                  <v-icon color="primary"
                    >mdi-checkbox-marked-circle-outline</v-icon
                  >
                  {{ '3 completed sessions' }}
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
                  task.taskDescription
                }}</v-list-item-subtitle>
                <p class="task-detail">
                  Duration:
                  {{
                    task.taskDuration !== 'None'
                      ? parseFloat(task.taskDuration).toFixed(2) + ' minutes'
                      : 'N/A'
                  }}
                </p>
                <p class="task-detail">
                  Measurements Selected:
                  <template v-if="task.measurementOptions.length > 0">
                    <v-chip
                      size="xsmall"
                      variant="outlined"
                      color="secondary"
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
                  factor.factorDescription
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
              hide-default-footer
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
                  class="me-2"
                  size="small"
                  @click.stop="openSession(item)"
                >
                  mdi-arrow-expand
                </v-icon>
                <v-icon size="small"> mdi-delete </v-icon>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-row justify="center">
      <v-col cols="auto">
        <v-btn @click="openNewSession" color="red">Start New Session</v-btn>
      </v-col>
    </v-row>
  </v-navigation-drawer>
</template>

<script>
import axios from 'axios'

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
      // sample data until the db is connected
      sessions: [
        {
          sessionName: 'Session 3',
          dateConducted: '11/22/2024',
          status: 'Valid',
          comment:
            'This is a sample comment of what the researcher may have written post-session.',
        },
        {
          sessionName: 'Session 2',
          dateConducted: '10/15/2024',
          status: 'Invalid',
          comment:
            'Another sample of comments that could be added to the details for a particular session.',
        },
        {
          sessionName: 'Session 1',
          dateConducted: '08/28/2024',
          status: 'Valid',
          comment:
            'The lack of creativity in these sample descriptions is superb.',
        },
      ],
    }
  },

  computed: {
    drawerProxy: {
      get() {
        // for reading the parent's value (in UserStudies.vue)
        return this.drawer
      },
      set(value) {
        // emits an update/notification to the parent
        this.$emit('update:drawer', value)
      },
    },
  },

  // watching for dynamic changes to the studyID and calls fetch route when it changes
  watch: {
    studyID: {
      immediate: true,
      handler(newStudyID) {
        if (newStudyID) {
          this.fetchStudyDetails(newStudyID)
        } else {
          console.warn('studyID not defined on mount')
        }
      },
    },
  },

  methods: {
    // retrieving all information on the study
    async fetchStudyDetails(studyID) {
      if (!studyID) {
        console.warn('No studyID to use as needed by the route')
        return
      }
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/load_study/${studyID}`
        const response = await axios.get(path)

        this.focus_study = response.data

        // HAVE THE COMPLETE AND ENTIRE STUDY FORMED HERE (focus_study)

        console.log(this.focus_study)

        this.studyName = this.focus_study.studyName
        this.studyDescription = this.focus_study.studyDescription || 'N/A'
        this.studyDesignType = this.focus_study.studyDesignType
        this.participantCount = this.focus_study.participantCount
        this.tasks = this.focus_study.tasks
        this.factors = this.focus_study.factors
      } catch (error) {
        console.error('Error fetching study details:', error)
      }
    },

    closeDrawer() {
      this.$emit('update:drawer', false)
    },

    editStudy() {
      return alert('Not implemented yet')
    },

    openSession() {
      this.$router.push('/SessionReporting')
    },

    getColor(status) {
      if (status == 'Invalid') {
        return 'red'
      } else {
        return 'green'
      }
    },

    // route to an empty study form page
    openNewSession() {
      this.$router.push('/SessionForm')
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
