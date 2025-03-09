<template>
  <v-main>
    <v-container class="mt-5">
      <v-row>
        <v-col cols="12">
          <h2>Studies</h2>
        </v-col>
      </v-row>

      <v-row justify="space-between" class="mb-4">
        <v-col cols="12" md="8" lg="9">
          <v-text-field
            v-model="search"
            label="Search"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            hide-details
            single-line
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="4" lg="3" class="d-flex justify-end">
          <v-btn class="create-study" color="primary" @click="openNewStudy">
            + Create New Study
          </v-btn>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12">
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
                  @click.stop="downloadStudyData(item.studyID)"
                >
                  mdi-download
                </v-icon>
                <v-icon
                  class="me-2"
                  size="small"
                  @click.stop="openDrawer(item.studyID)"
                >
                  mdi-arrow-expand
                </v-icon>
                <v-icon
                  v-if="item.canEdit"
                  class="me-2"
                  size="small"
                  @click.stop="editExistingStudy(item.studyID)"
                >
                  mdi-file-document-edit
                </v-icon>
                <v-icon
                  class="me-2"
                  size="small"
                  @click.stop="copyStudy(item.studyID)"
                >
                  mdi-content-copy
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
        v-if="drawer && selectedStudy.studyID"
        :drawer="drawer"
        :studyID="selectedStudy.studyID"
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
      // holds all the studies returned from db query
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
    const path = `${backendUrl}/get_study_data/${userID}`
    const response = await axios.get(path)

    if (Array.isArray(response.data)) {
      this.studies = await Promise.all(
        response.data.map(async (study) => {
          const canEdit = await this.checkIfOverwriteAllowed(userID, study[1])
          return {
            dateCreated: study[0],
            studyID: study[1],
            studyName: study[2],
            studyDesc: study[3],
            sessionCount: study[4],
            role: study[5],
            canEdit: canEdit, // Add the flag to the study object
          }
        })
      )
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
    openDrawer(studyID) {
      this.selectedStudy = { studyID }
      this.drawer = true
    },

    // dynamic confirmation for study deletion
    displayDialog(details) {
      this.dialogDetails = { ...details }
      this.dialog = true
    },
    async downloadStudyData(studyID) {
    try {
      const backendUrl = this.$backendUrl
      const path = `${backendUrl}/get_all_session_data_instance_zip/${studyID}`

      const response = await axios.get(path, {
        responseType: 'blob'
      })

      // Get the content-disposition header to extract the filename
      const disposition = response.headers['content-disposition']
      const filename = disposition
        ? disposition.split('filename=')[1].replace(/"/g, '')  // extracting the filename from header
        : 'download.zip'

      // Download
      const blob = new Blob([response.data], { type: 'application/zip' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = filename
      link.click()

    } catch (error) {
      console.error('Error downloading study data:', error)
    }
  },
  async checkIfOverwriteAllowed(userID, studyID) {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/is_overwrite_study_allowed/${userID}/${studyID}`
        const response = await axios.get(path);
        
        if (response.data === true) {
          return true
        } else {
          return false
        }
      } catch (error) {
        console.error("Error checking overwrite permission:", error);
        this.isButtonVisible = false;  // Hide the button if there's an error
      }
    },
    async copyStudy(studyID) {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/copy_study/${studyID}/${1}`
        const response = await axios.post(path);

        // Refresh the page to show changes
        location.reload()
        
      } catch (error) {
        console.error("Error copying study", error);
        this.isButtonVisible = false;  // Hide the button if there's an error
      }
    },
  editExistingStudy(study_id) {
      this.$router.push({
        name: 'StudyForm',
        params: { studyID: study_id, userID: 1 }, // 1 is hardcoded for now until we have users
      })
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

<style scoped>
.create-study {
  font-size: 16px;
  font-weight: bold;
  padding: 10px 20px;
  text-transform: none;
}

.study-name {
  display: flex;
  align-items: center;
}

.table-background {
  background-color: #ffffff !important;
}

.v-text-field {
  width: 100%;
}

.v-btn.block {
  width: 100%;
}

h2 {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 16px;
}

.mb-4 {
  margin-bottom: 16px !important;
}

.d-flex {
  display: flex !important;
}

.justify-end {
  justify-content: flex-end !important;
}
</style>
