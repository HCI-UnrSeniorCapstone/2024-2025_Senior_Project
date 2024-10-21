<template>
  <div>
    <v-btn color="secondary" @click="getMessage">{{msg}}</v-btn>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  name: 'Ping',
  data() {
    return {
      msg: 'Hello!',
    };
  },
  methods: {
    getMessage() {
      const path = 'http://localhost:5001/ping';
      axios.get(path)
      .then((res) => {
        this.msg = res.data;
      })
      .catch((error) => {
        console.error(error);
      });
    },
  },
  created() {
    this.getMessage();
  },
};
</script>
