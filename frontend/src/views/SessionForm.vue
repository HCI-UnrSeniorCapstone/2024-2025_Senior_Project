<template>
  <v-btn @click="startSession" color="green">Begin Session</v-btn>
</template>

<script>
// export default{
//   data() {
//     return [

//     ]
//   }

// }
// async startSession() {
//   // gets demo2.json file from the public folder. This is temp, will be pushing this to the DB and soon fetch from the DB
//   //https://testdriven.io/blog/combine-flask-vue/
//   const backendUrl = this.$backendUrl
//   const path = `${backendUrl}/get_data`
//   // NOTE: this user_id is hardcoded in the config.json for now but need to be updated
//   const response = await fetch(path / '${this.user_id}') //server flask
//   const userData = await response.json()
//   // console.log(userData);
//   alert(JSON.stringify(userData, null, 2))
//   try {
//     const response = axios.post('http://127.0.0.1:5001/run_study', userData) //local flask
//     console.log('Response:', response.data)
//   } catch (error) {
//     console.error('Error: ', error)
//   }
// }
</script>
