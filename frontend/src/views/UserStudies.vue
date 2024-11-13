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
            >
              <template v-slot:item.studyName="{ item }">
                <div class="study-name">
                  {{ item.studyName }}
                  <v-icon class="expand-study" size="small" @click.stop="openDrawer(item.studyName)">mdi-arrow-expand</v-icon>
                </div>
              </template>
              <template v-slot:item.progress="{ item }">
                <v-progress-linear
                  :model-value="calculateProgress(item.completedSessions, item.expectedSessions)"
                  height="15"
                  color="primary"
                >
                  <strong>{{ calculateProgress(item.completedSessions, item.expectedSessions) }}%</strong>
                </v-progress-linear>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
      <v-navigation-drawer
        v-model="drawer"
        location="right"
        temporary
        :width="1000"
      >
        <v-toolbar flat dense>
          <v-toolbar-title>{{ drawerTitle }}</v-toolbar-title>
        </v-toolbar>
        <v-row justify="center">
          <v-col cols="auto">
              <v-btn @click="startSession" class="start-session" type="startSession" color="red">Start Session</v-btn>
          </v-col>
        </v-row>
      </v-navigation-drawer>
    </v-container>
  </v-main>
</template>

<script>
  import axios from 'axios'
  import userData from 'C:/Users/jairo/OneDrive/Desktop/capstone/2024-2025_Senior_Project/demo2.json'


  export default {
    data () {
      return {
        search: '',
        drawer: false,
        drawerTitle: '',
        headers: [
          {
            align: 'start',
            key: 'studyName',
            sortable: false,
            title: 'User Study Name',
          },
          { key: 'studyDesc', title: 'Description', sortable: false},
          { key: 'completedSessions', title: '# Completed Sessions', sortable: false, width: "120px" },
          { key: 'dateCreated', title: 'Date Created', sortable: false },
          { key: 'progress', title: 'Progress', sortable: false, width: "200px" },
          { key: 'permissions', title: 'Permissions', sortable: false },
        ],
        studies: [
          {
            studyName: 'User Interface Friendliness for Elderly People',
            studyDesc: 'Explores the usability of interfaces designed for older adults.',
            completedSessions: 10,
            expectedSessions: 15,
            dateCreated: '2024-04-05',
            permissions: 'Read/Write',
          },
          {
            studyName: 'Virtual Reality in Educational Environments',
            studyDesc: 'Investigates how VR can enhance learning experiences in classrooms.',
            completedSessions: 8,
            expectedSessions: 10,
            dateCreated: '2024-02-20',
            permissions: 'Read/Write',
          },
          {
            studyName: 'Eye-Tracking for User Attention Analysis',
            studyDesc: 'Uses eye-tracking technology to assess user attention on e-commerce sites.',
            completedSessions: 16,
            expectedSessions: 17,
            dateCreated: '2023-12-09',
            permissions: 'Read/Write',
          },
          {
            studyName: 'Voice Interface Usability in Noisy Environments',
            studyDesc: 'Examines the usability of voice-activated systems in high-noise settings.',
            completedSessions: 15,
            expectedSessions: 15,
            dateCreated: '2023-10-10',
            permissions: 'Read/Write',
          },
        ],
      }
    },

    methods : {
      openNewStudy () {
        this.$router.push('/StudyForm')
      },
      calculateProgress(completed, expected) {
        let percentVal = Math.floor((completed / expected) * 100);
        return percentVal
      },
      openDrawer(studyName) {
        this.drawerTitle = studyName;
        this.drawer = true;
      },
      // **********************FOR DEMO USE ONLY****************
      async startSession() {
        const submissionData = {
          studyName: "sup foo",
          studyDescription: "",
          studyDesignType: "",
          participantCount: "",
          tasks: [{
            taskName: "Tracking mouse",
            taskDescription: "",
            taskDuration: 5,
            measurementOptions: ["Mouse Movement", "Mouse Click", "Mouse Scrolls"]
          },
          {
            taskName: "Keyboard Tracking",
            taskDescription: "",
            taskDuration: 5,
            measurementOptions: ["Keyboard Inputs"]
          }],
          // factors: this.factors.map(factor => ({
          //   factorName:"",
          //   factorDescription: ""
          // }
          // )),
        };

        // alert('test');

        // const json_data = require("./2024-2025_Senior_Project/demo2.json")
        alert(JSON.stringify(userData, null, 2));

        try {
          const response = await axios.post('http://localhost:5000/testing', userData);
          console.log('Response:', response.data);
        } catch (error) {
          console.error("Error: ", error)
        }
      },
      // ************************************************************
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
  .start-session {
    margin-top: 300px;
  }
  .expand-study {
    margin-left: 5px;
  }
</style>
