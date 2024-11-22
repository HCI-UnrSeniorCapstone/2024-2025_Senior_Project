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
          <v-btn class="create-study" @click="openNewStudy">+ Create New Study</v-btn>
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
                  {{ item.studyDesc.length > 100 ? item.studyDesc.substring(0, 100) + '...' : item.studyDesc }}
                </div>
              </template>
              <template v-slot:item.sessionCount="{ item }">
                <div>
                  {{ item.sessionCount + '/' + item.expectedNumParticipants }}
                </div>
              </template>
              <template v-slot:item.progress="{ item }">
                <v-progress-linear
                  :model-value="calculateProgress(item.sessionCount, item.expectedNumParticipants)"
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

    </v-container>
  </v-main>
</template>

<script>
  import StudyPanel from './StudyPanel.vue';

  export default {

    components: { StudyPanel },

    data () {
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
          { key: 'studyName', title: 'User Study Name', sortable: false, width: "250px" },
          { key: 'studyDesc', title: 'Description', sortable: false},
          { key: 'sessionCount', title: 'Sessions', sortable: false },
          { key: 'progress', title: 'Progress', sortable: false, width: "200px" },
          { key: 'role', title: 'Role', sortable: false },
          { key: 'actions', title: 'Actions', sortable: false },
        ],
        // sample data until the db is connected 
        studies: [
          {
            studyName: 'UI Elderly Friendliness',
            studyDesc: 'Explores the usability of interfaces designed for older adults.',
            sessionCount: 10,
            expectedNumParticipants: 15,
            dateCreated: '04/04/2024',
            role: 'Author',
          },
          {
            studyName: 'VR in Educational',
            studyDesc: 'Investigates how VR can enhance learning experiences in classrooms by conducting tests with teenagers...',
            sessionCount: 8,
            expectedNumParticipants: 10,
            dateCreated: '02/20/2024',
            role: 'Author',
          },
          {
            studyName: 'Attention Analysis',
            studyDesc: 'Uses eye-tracking technology to assess user attention on e-commerce sites.',
            sessionCount: 16,
            expectedNumParticipants: 17,
            dateCreated: '12/09/2023',
            role: 'Editor',
          },
          {
            studyName: 'Voice Interface Usability',
            studyDesc: 'Examines the usability of voice-activated systems in high-noise settings.',
            sessionCount: 15,
            expectedNumParticipants: 15,
            dateCreated: '10/10/2023',
            role: 'Viewer',
          },
        ],
      }
    },

    methods : {
      // route to an empty study form page
      openNewStudy () {
        this.$router.push('/StudyForm')
      },
      // used to display progress in the table progress bars 
      calculateProgress(completed, expected) {
        let percentVal = Math.floor((completed / expected) * 100);
        return percentVal
      },
      // toggle drawer open and bind study-specific info to populate the right panel 
      openDrawer(study) {
        this.selectedStudy = { ...study};
        this.drawer = true;
      },
    }
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
