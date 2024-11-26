<template>
  <v-main>
    <v-container class="mt-5">
      <v-row>
        <v-col cols="12">
          <h2>Studies</h2>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="7">
          <v-text-field
            v-model="search"
            label="Search"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            hide-details
            single-line
          ></v-text-field>
        </v-col>
        <v-spacer></v-spacer>
        <v-col cols="2">
          <v-btn class="create-study" @click="openNewStudy"
            >+ Create New Study</v-btn
          >
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" md="12">
          <v-card flat>
            <v-data-table
              :headers="headers"
              :items="studies"
              :search="search"
              class="table-background"
            >
              <template v-slot:item.studyName="{ item }">
                <div class="study-name">
                  {{ item.studyName }}
                </div>
              </template>
              <template v-slot:item.studyDesc="{ item }">
                <div>
                  {{
                    item.studyDesc.length > 100
                      ? item.studyDesc.substring(0, 100) + '...'
                      : item.studyDesc
                  }}
                </div>
              </template>
              <template v-slot:item.sessionCount="{ item }">
                <div>
                  {{ item.sessionCount }}
                </div>
              </template>
              <template v-slot:item.progress="{ item }">
                <v-progress-linear
                  :model-value="calculateProgress(item.sessionCount)"
                  height="15"
                  color="primary"
                >
                </v-progress-linear>
              </template>
              <template v-slot:item.actions="{ item }">
                <v-icon
                  class="me-2"
                  size="small"
                  @click.stop="openDrawer(item)"
                >
                  mdi-arrow-expand
                </v-icon>
                <v-icon
                  size="small"
                  @click="
                    displayDialog({
                      title: 'Delete Study?',
                      text: 'Are you sure you want to delete this study?',
                      studyID: item.studyID,
                    })
                  "
                >
                  mdi-delete
                </v-icon>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>

      <StudyPanel
        :drawer="drawer"
        :study="selectedStudy"
        @update:drawer="drawer = $event"
        @close="drawer = false"
      />

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

              <v-btn @click="closeDialog('yes')"> Agree </v-btn>
            </template>
          </v-card>
        </v-dialog>
      </div>
    </v-container>
  </v-main>
</template>

<script>
import StudyPanel from './StudyPanel.vue'
import axios from 'axios'

export default {
  components: { StudyPanel },

  data() {
    return {
      search: '',
      drawer: false,
      selectedStudy: {},
      headers: [
        {
          align: 'start',
          key: 'dateCreated',
          sortable: false,
          title: 'Date Created',
        },
        {
          key: 'studyName',
          title: 'User Study Name',
          sortable: false,
          width: '250px',
        },
        { key: 'studyDesc', title: 'Description', sortable: false },
        { key: 'sessionCount', title: 'Sessions', sortable: false },
        { key: 'progress', title: 'Progress', sortable: false, width: '200px' },
        { key: 'role', title: 'Role', sortable: false },
        { key: 'actions', title: 'Actions', sortable: false },
      ],
      // dialog box for user confirmation
      dialog: false,
      dialogDetails: {
        title: '',
        text: '',
        study: '',
      },
      // sample data until the db is connected
      studies: [],
    }
  },

  //populate table on page load w/ a temporary hardcoded userID of 1
  mounted() {
    this.populateStudies(1)
  },

  methods: {
    // populating the studies table
    async populateStudies(userID) {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/get_data/${userID}`
        const response = await axios.get(path)

        if (Array.isArray(response.data)) {
          this.studies = response.data.map(study => ({
            dateCreated: study[0],
            studyID: study[1],
            studyName: study[2],
            studyDesc: study[3],
            sessionCount: study[4],
            role: study[5],
          }))
        }
      } catch (error) {
        console.error('Error retrieving studies: ', error)
      }
    },

    // route to an empty study form page
    openNewStudy() {
      this.$router.push('/StudyForm')
    },

    // used to display progress in the table progress bars
    calculateProgress(sessionCount) {
      const [completed, expected] = sessionCount.split('/').map(Number)
      let percentVal = Math.floor((completed / expected) * 100)
      return percentVal
    },

    // toggle drawer open and bind study-specific info to populate the right panel
    openDrawer(study) {
      this.selectedStudy = { ...study }
      this.drawer = true
    },

    // dynamic confirmation for study deletion
    displayDialog(details) {
      this.dialogDetails = { ...details }
      this.dialog = true
    },

    // impacts whether we actually delete the study or not based on the user input
    async closeDialog(choice) {
      if (choice == 'yes') {
        const studyID = this.dialogDetails.studyID
        const userID = 1 //temp

        try {
          const backendUrl = this.$backendUrl
          const path = `${backendUrl}/delete_study/${studyID}/${userID}` // passing study and user id to tell what to "delete"
          const response = await axios.post(path)
          this.studies = this.studies.filter(study => study.studyID !== studyID) //removing from local studies list
        } catch (error) {
          console.error('Error:', error.response?.data || error.message)
        }
      }
      this.dialog = false
    },
  },
}
</script>

<style>
.create-study {
  min-width: 100px;
  min-height: 50px;
}
.study-name {
  display: flex;
  align-items: center;
}
.expand-study {
  margin-left: 5px;
}
.table-background {
  background-color: #ffffff !important;
}
</style>
