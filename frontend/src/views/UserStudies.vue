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
          <SearchBar v-model="search" />
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
                  v-tooltip="'Download Results'"
                  class="me-2"
                  size="small"
                  @click.stop="downloadStudyData(item.studyID)"
                >
                  mdi-download
                </v-icon>
                <v-icon
                  v-tooltip="'Open'"
                  class="me-2"
                  size="small"
                  @click.stop="openDrawer(item.studyID)"
                >
                  mdi-arrow-expand
                </v-icon>
                <v-icon
                  v-if="item.canEdit"
                  v-tooltip="'Edit'"
                  class="me-2"
                  size="small"
                  @click.stop="editExistingStudy(item.studyID)"
                >
                  mdi-pencil
                </v-icon>
                <v-icon
                  v-tooltip="'Duplicate'"
                  class="me-2"
                  size="small"
                  @click.stop="duplicateStudy(item.studyID)"
                >
                  mdi-content-copy
                </v-icon>
                <v-icon
                  v-tooltip="'Delete'"
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
        v-if="drawer && studyStore.drawerStudyID"
        :drawer="drawer"
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
import StudyPanel from '@/components/StudyPanel.vue'
import SearchBar from '@/components/SearchBar.vue'
import api from '@/axiosInstance'
import { useStudyStore } from '@/stores/study'
export default {
  components: { StudyPanel, SearchBar },
  setup() {
    const studyStore = useStudyStore()
    return { studyStore }
  },
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
      dialog: false,
      dialogDetails: { title: '', text: '', study: '' },
      studies: [],
    }
  },

  async mounted() {
    const studyStore = useStudyStore()
    studyStore.clearSessionJson() // Incase we quit during a session, we reset this
    if (studyStore.drawerStudyID) {
      this.openDrawer(studyStore.drawerStudyID)
    }
    await this.populateStudies()
    const studyID = this.$route.query.studyID
    if (studyID) {
      this.openDrawer(Number(studyID))
    }
  },

  watch: {
    drawer(newVal) {
      if (!newVal && this.$route.query.studyID) {
        this.$router.replace({
          query: { ...this.$route.query, studyID: undefined },
        })
      }
    },
  },

  methods: {
    async populateStudies() {
      try {
        const response = await api.get('/get_study_data')

        if (Array.isArray(response.data)) {
          this.studies = await Promise.all(
            response.data.map(async study => {
              const canEdit = await this.checkIfOverwriteAllowed(study[1])
              return {
                dateCreated: study[0],
                studyID: study[1],
                studyName: study[2],
                studyDesc: study[3],
                sessionCount: study[4],
                role: study[5],
                canEdit: canEdit,
              }
            }),
          )
        }
      } catch (error) {
        console.error('Error retrieving studies: ', error)
      }
    },

    openNewStudy() {
      const studyStore = useStudyStore()
      studyStore.clearStudyID()
      // studyStore.clearDrawerStudyID?.() // optional: in case drawer was open
      sessionStorage.removeItem('currentStudyID')
      studyStore.incrementFormResetKey()

      this.$router.push({ name: 'StudyForm' })
    },

    calculateProgress(sessionCount) {
      const [completed, expected] = sessionCount.split('/').map(Number)
      let percentVal = Math.floor((completed / expected) * 100)
      return percentVal
    },

    openDrawer(studyID) {
      const match = this.studies.find(study => study.studyID == studyID)
      if (match) {
        const studyStore = useStudyStore()

        this.selectedStudy = match
        this.drawer = true
        studyStore.setDrawerStudyID(match.studyID)
      }
    },

    displayDialog(details) {
      this.dialogDetails = { ...details }
      this.dialog = true
    },

    async downloadStudyData(studyID) {
      try {
        const path = `/get_all_session_data_instance_zip`
        const response = await api.post(
          path,
          { study_id: studyID },
          { responseType: 'blob' },
        )

        const disposition = response.headers['content-disposition']
        const filename = disposition
          ? disposition.split('filename=')[1].replace(/"/g, '')
          : 'download.zip'

        const blob = new Blob([response.data], { type: 'application/zip' })
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = filename
        link.click()
      } catch (error) {
        console.error('Error downloading study data:', error)
      }
    },

    async checkIfOverwriteAllowed(studyID) {
      try {
        const payload = { studyID: studyID } // Pass studyID in the request body
        const response = await api.post('/is_overwrite_study_allowed', payload)

        if (response.data === true) {
          return true
        } else {
          return false
        }
      } catch (error) {
        console.error('Error checking overwrite permission:', error)
        this.isButtonVisible = false
      }
    },

    async duplicateStudy(studyID) {
      try {
        const payload = { studyID: studyID }
        const response = await api.post('/copy_study', payload)

        // Refresh the page to show changes
        location.reload()
      } catch (error) {
        console.error('Error copying study', error)
      }
    },

    editExistingStudy(studyID) {
      const studyStore = useStudyStore()
      studyStore.setStudyID(studyID)
      studyStore.incrementFormResetKey()
      this.$router.push({ name: 'StudyForm' })
    },

    async closeDialog(choice) {
      if (choice == 'yes') {
        const studyID = this.dialogDetails.studyID

        try {
          const response = await api.post(`/delete_study`, { studyID })
          this.studies = this.studies.filter(study => study.studyID !== studyID)
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
