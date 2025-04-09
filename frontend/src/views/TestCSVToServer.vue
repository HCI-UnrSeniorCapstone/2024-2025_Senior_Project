<template>
  <div>
    <v-btn color="primary" @click="handleFileUpload">{{ msg }}</v-btn>
    <input type="file" @change="onFileChange" />
    <div v-if="results.length > 0">
      <h3>User Data:</h3>
      <ul></ul>
    </div>
    <div v-else>
      <p>No data found.</p>
    </div>
  </div>
</template>

<script>

import api from '@/axiosInstance'

export default {
  name: 'TestSendCSV',
  data() {
    return {
      msg: 'Upload CSV File',
      results: [],
      file: null,
    }
  },
  methods: {
    onFileChange(event) {
      this.file = event.target.files[0]
    },

    // upload the file
    handleFileUpload() {
      if (!this.file) {
        this.msg = 'Please select a file first!'
        return
      }

      const formData = new FormData()
      formData.append('input_csv', this.file) // Append the selected file

      const path = `/save_session_data_instance/1/1/1/1/1` //HARDCODED Parameters to show proof of concept
      axios
        .post(path, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        .then(res => {
          console.log(res.data)
          this.msg = res.data.message || 'File uploaded successfully'
        })
        .catch(error => {
          console.error('Error uploading file:', error)
          this.msg = 'Error uploading file'
        })
    },
  },
}
</script>
