<template>
  <v-main>
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="6">
          <form @submit.prevent="submit">
            <h2>Study Details</h2>
            <v-text-field
              v-model="studyName.value.value"
              :counter="25"
              label="Study Name *"
              :error-messages="studyName.errorMessage.value"
              required
            ></v-text-field>

            <v-text-field
              v-model="studyDescription.value.value"
              :counter="250"
              label="Study Description"
              :error-messages="studyDescription.errorMessage.value"
            ></v-text-field>

            <v-row dense>
              <v-col cols="12" md="6">
                <v-date-input
                  v-model="startDate.value.value"
                  label="Start Date"
                  prepend-icon=""
                  prepend-inner-icon="$calendar"
                ></v-date-input>
              </v-col>
              <v-col cols="12" md="6">
                <v-date-input
                  v-model="endDate.value.value"
                  label="End Date"
                  prepend-icon=""
                  prepend-inner-icon="$calendar"
                ></v-date-input>
              </v-col>
            </v-row>
            
            <h3>Tasks</h3>
            <v-expansion-panels multiple>
              <v-expansion-panel v-for="(task,index) in tasks" :key="index">
                <v-expansion-panel-title>
                  <template v-slot:default= "{ open }">
                    <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                      <span>{{ task.taskName || 'Task ' + (index+1) }}</span>
                      <div class="move-arrows">
                        <v-btn icon @click.stop="slideTaskUp(index)" :disabled="index === 0" size="x-small" class="individual-arrow">
                          <v-icon icon="mdi-arrow-up" size="x-small"></v-icon>
                        </v-btn>
                        <v-btn icon @click.stop="slideTaskDown(index)" :disabled="index === tasks.length - 1" size="x-small" class="individual-arrow">
                          <v-icon icon="mdi-arrow-down" size="x-small"></v-icon>
                        </v-btn>
                      </div>
                    </div>
                  </template>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <task
                    :task="task"
                    @remove="() => removeTask(index)"
                  />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
            <v-container>
              <v-btn @click="addTask" color="grey" class="add-task">
                <v-icon left>mdi-plus</v-icon>
                Add Task
              </v-btn>
            </v-container>
            <v-row class="btn-row">
              <v-btn class="me-4 btn-exit">Exit</v-btn>
              <v-btn class="me-4 btn-submit" type="submit">Submit</v-btn>
            </v-row>
          </form>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>
  
<script setup>
  import { ref } from 'vue';
  import { useField, useForm} from 'vee-validate'
  import { VDateInput } from 'vuetify/labs/VDateInput'
  import Task from '../components/Task.vue'
  import axios from 'axios';

  const { handleSubmit} = useForm({
    validationSchema: {
      studyName (value) {
        if (value?.length < 2) {
            return 'Study name needs to be at least 2 characters.';
        }
        else if (value?.length > 25) {
            return 'Study name exceeds character limit.';
        }
        
        return true;
        },
        studyDescription (value) {
        if (value && value.length > 250){
          return 'Task description exceeds character limit.'
        }
        return true;

        },
    },  
  });

  const studyName = useField('studyName');
  const studyDescription = useField('studyDescription');
  const tasks = ref([]);
  const startDate = useField('startDate');
  const endDate = useField('endDate');


  const addTask = () => {
    tasks.value.push({ taskName: '', taskDescription: '', taskDuration: '', measurementTypes: [] });
  };

  const removeTask = index => { 
    tasks.value.splice(index, 1);
  };

  const slideTaskDown = index => {
    if(index < tasks.value.length - 1){
      const tempTask = tasks.value[index];
      tasks.value[index] = tasks.value[index + 1];
      tasks.value[index + 1] = tempTask;    
    }
  };

  const slideTaskUp = index => {
    if(index > 0){
      const tempTask = tasks.value[index];
      tasks.value[index] = tasks.value[index - 1];
      tasks.value[index - 1] = tempTask;    
    }
  };

  const submit = handleSubmit(async () => {
    const submissionData = {
      studyName: studyName.value.value,
      studyDescription: studyDescription.value.value || '',
      startDate: startDate.value.value ? new Date(startDate.value.value).toISOString().split('T')[0] : '',
      endDate: endDate.value.value ? new Date(endDate.value.value).toISOString().split('T')[0] : '',
      tasks: tasks.value.map(task => ({
        taskName: task.taskName,
        taskDescription: task.taskDescription,
        taskDuration: task.taskDuration,
        measurementTypes: [...task.measurementTypes]
      }))
    };
    alert(JSON.stringify(submissionData, null, 2));

    const response = await axios.post('http://localhost:5000/start_tracking', submissionData);
    console.log('Response:', response.data);
  });
    
</script>

<style scoped>
  .move-arrows {
    margin-right: 20px;
  }
  .individual-arrow {
    margin-left: 2px;
    margin-right: 2px;
  }
  .btn-exit, .btn-submit {
    flex: 1;
    margin: 5px;
  }
  .btn-row {
    display: flex;
    justify-content: space-between;
    padding: 10px 100px;
  }
  .add-task {
    max-height: 22px;
    min-width: 100px;
  }
</style>