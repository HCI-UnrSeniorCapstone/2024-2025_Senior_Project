<template>
  <v-navigation-drawer
    v-model="drawerProxy"
    location="right"
    temporary
    :width="1000"
  >
    <v-toolbar flat dense color="white">
      <v-toolbar-title> {{ study.studyName }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="editStudy">
          <v-icon color="secondary">mdi-pencil</v-icon>
      </v-btn>
      <v-btn icon @click="closeDrawer">
          <v-icon color="secondary">mdi-close</v-icon>
      </v-btn>
    </v-toolbar>
    <v-divider class="mb-2"></v-divider>

    <v-container class="py-4">
      <v-row class="mb-3">
        <v-col  cols="12">
          <h4>Description</h4>
          <p> {{ study.studyDesc }}</p>
          <v-divider class="mb-2"></v-divider>
          <p><strong># Tasks: </strong>4</p>
          <p><strong># Factors: </strong>2</p>
          <v-divider class="mb-2"></v-divider>
        </v-col>
      </v-row>

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
                  {{ item.comment.length > 100 ? item.comment.substring(0, 100) + '...' : item.comment }}
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

      <v-row justify="center">
        <v-col cols="auto">
            <v-btn
              @click="startSession"
              type="startSession"
              color="red"
            >Start Session</v-btn>
        </v-col>
      </v-row>
    </v-container>
  
  </v-navigation-drawer>
</template>

<script>
  export default {
    props: {
      drawer: {
        type: Boolean,
        required: true
      },
      study: {
        type: Object,
        required: true,

      }
    },

    data () {
      return {
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
            comment: 'This is a sample comment of what the researcher may have written post-session.'
          },
          {
            sessionName: 'Session 2',
            dateConducted: '10/15/2024',
            status: 'Invalid',
            comment: 'Another sample of comments that could be added to the details for a particular session.'
          },
          {
            sessionName: 'Session 1',
            dateConducted: '08/28/2024',
            status: 'Valid',
            comment: 'The lack of creativity in these sample descriptions is superb.'
          },
        ],
      }
    },

    computed: {
      drawerProxy: {
        get() { // for reading the parent's value (in UserStudies.vue)
          return this.drawer;
        },
        set(value) { // emits an update/notification to the parent 
          this.$emit("update:drawer", value);
        }
      }
    },

    methods: {

      closeDrawer() {
        this.$emit("update:drawer", false)
      },

      editStudy() {
        return alert("Not implemented yet");
      },

      openSession () {
        this.$router.push('/SessionReporting')
      },

      getColor (status) {
        if (status == 'Invalid') {
          return 'red'; 
        }
        else {
          return 'green';
        }
      },

      // **********************FOR DEMO USE ONLY****************
      async startSession() {
      // gets demo2.json file from the public folder. This is temp, will be pushing this to the DB and soon fetch from the DB
      const response = await fetch('/demo2.json');
      const userData = await response.json();
      alert(JSON.stringify(userData, null, 2));
      try {
        const response = await axios.post('http://localhost:5000/run_study', userData);
        console.log('Response:', response.data);
      } catch (error) {
        console.error("Error: ", error)
      }
      },
      // ************************************************************
    }

  };
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
  }

</style>