<template>
  <div>
    <p>Received Variable: {{ studyId }}</p>
  </div>
  <div class="container">
    <v-btn @click="getSessionID()" color="green">Begin Session</v-btn>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      studyId: null,
      participantSessId: null,
      study: null,
    }
  },

  mounted() {
    this.studyId = this.$route.params.id
    this.getStudyInfo()
  },

  methods: {
    // identical to fetchStudyData() on StudyPanel.vue
    // decided best to query using passed study id rather than send study object to this vue
    // we could miss recent changes to the study if we pass the obj, plus passing phat objects around isnt good
    async getStudyInfo() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/load_study/${this.studyId}`
        const response = await axios.get(path)

        this.study = response.data

        console.log(this.study)
      } catch (error) {
        console.error('Error fetching study details:', error)
      }
    },

    async getSessionID() {
      try {
        const backendUrl = this.$backendUrl
        const path = `${backendUrl}/create_participant_session/${this.studyId}`
        const response = await axios.post(path, {
          participantGender: 'Male',
          participantEducationLv: 'Some College',
          participantAge: 25,
          participantRaceEthnicity: ['Asian', 'White'],
          participantTechCompetency: 5,
        })
        this.participantSessId = response.data.participant_session_id
        console.log('Session ID: ', this.participantSessId)
        if (this.participantSessId) {
          // only allow the session to start and info the be passed to local flask if participant id is available
          this.study.participantSessId = this.participantSessId
          this.study.study_id = this.studyId

          await this.startSession()

          //********* WORK IN PROGRESS ******************************//
          // const default_measurment_id = {"Mouse Movement": 1, "Mouse Scrolls": 2, "Mouse Clicks": 3, "Keyboard Inputs": 4}
          // console.log(this.study.tasks[0].taskName) //gets the task name
          // console.log(this.study.factors[0].factorName) //gets factor name
          // console.log(this.study.tasks[0].measurementOptions[0]) //gets the measurment name
          //participantSessId
          //study_id
          // console.log(this.study.tasks[0].taskID) //gets the task id
          // console.log(default_measurment_id["Mouse Scrolls"]) //gets the measurment id
          // console.log(this.study.factors[0].factorID) //gets the factor id

          // for(let i = 0; i < this.study.tasks.length; i++){
          //   console.log(this.study.tasks[i].measurementOptions[i])
          //   if(this.study.tasks[i].measurementOptions[i] == 'Mouse Scrolls' || this.study.tasks[i].measurementOptions[i] == 'Mouse Movement' || this.study.tasks[i].measurementOptions[i] == 'Mouse Clicks'){
          //     const csv_path = `./${this.study.tasks[i].taskName}_${this.study.factors[i].factorName}_${this.study.tasks[i].measurementOptions[i]}_${this.study.participantSessId}_${this.study.study_id}_${this.study.tasks[i].taskID}_${default_measurment_id['Mouse Scrolls']}_${this.study.factors[i].factorID}.csv`
          //     console.log(csv_path)

          //     const file = new File([this.getFileBlob_mouse(csv_path)], 'file.csv', { type: 'text/csv' })

          //     const formData = new FormData()
          //     formData.append('input_csv', this.file) // Append the selected file

          //     const backendUrl = this.$backendUrl
          //     const path = `${backendUrl}/save_session_data_instance/${this.study.participantSessId}/${this.study.study_id}/${this.study.tasks[i].taskID}/${default_measurment_id[this.study.tasks[i].measurementOptions[i]]}/${this.study.factors[i].factorID}`
          //     axios
          //       .post(path, formData, {
          //         headers: {
          //           'Content-Type': 'multipart/form-data',
          //         },
          //       })
          //   }
          //   else if (this.study.tasks[i].measurementOptions[i] == 'Keyboard Inputs'){
          //     const csv_path = `./${this.study.tasks[i].taskName}_${this.study.factors[i].factorName}_${this.study.tasks[i].measurementOptions[i]}_${this.study.participantSessId}_${this.study.study_id}_${this.study.tasks[i].taskID}_${default_measurment_id['Keyboard Inputs']}_${this.study.factors[i].factorID}.csv`
          //     console.log(csv_path)

          //     const file = new File([this.getFileBlob_mouse(csv_path)], 'file.csv', { type: 'text/csv' })

          //     const formData = new FormData()
          //     formData.append('input_csv', this.file)

          //     const backendUrl = this.$backendUrl
          //     const path = `${backendUrl}/save_session_data_instance/${this.study.participantSessId}/${this.study.study_id}/${this.study.tasks[i].taskID}/${default_measurment_id[this.study.tasks[i].measurementOptions[i]]}/${this.study.factors[i].factorID}`
          //     axios
          //       .post(path, formData, {
          //         headers: {
          //           'Content-Type': 'multipart/form-data',
          //         },
          //       })
          //   }
          // }

          //********* WORK IN PROGRESS ******************************//

        }
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
      }
    },

    async startSession() {
      try {
        const path = 'http://127.0.0.1:5001/run_study'
        const response = await axios.post(path, this.study)
      } catch (error) {
        console.error('Error:', error.response?.data || error.message)
      }
    },
    getFileBlob_mouse(filePath) {
      try {
        // Example: Convert file content to Blob (assuming CSV data is to be fetched/generated)
        const csvContent = `data:text/csv;charset=utf-8,Time,running_time,x,y`;

        return new Blob([csvContent], { type: 'text/csv' });
      } catch (error) {
        console.error('Error creating Blob:', error);
        return null;
      }
    },
    getFileBlob_keyboard(filePath) {
      try {
        // Example: Convert file content to Blob (assuming CSV data is to be fetched/generated)
        const csvContent = `data:text/csv;charset=utf-8,Time,running_time,keys`;

        return new Blob([csvContent], { type: 'text/csv' });
      } catch (error) {
        console.error('Error creating Blob:', error);
        return null;
      }
    },
  },
}
</script>


<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
</style>
