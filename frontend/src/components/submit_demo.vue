<!-- <template>
  <div>
    <v-btn color="secondary" @click="getdata">{{msg}}</v-btn>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  name: 'start tracking',
  // data() {
  //   return {
  //     msg: 'Hello!',
  //   };
  // },
  methods: {
    getdata() {
      const path = 'http://localhost:5001/start_tracking';
      axios.get(path)
      // .then((res) => {
      //   this.msg = res.data;
      // })
      // .catch((error) => {
      //   console.error(error);
      // });
    },
  },
  // created() {
  //   this.getMessage();
  // },
};
</script> -->


<template>
  <button @click="sendData">Send Data</button>
</template>

<script>
export default {
  methods: {
    sendData() {
      const data = { message: "Hello from Vue!" };
      this.axios.post('/api/endpoint', data)
        .then(response => {
          console.log(response.data);
        })
        .catch(error => {
          console.error(error);
        });
    }
  }
}
</script>