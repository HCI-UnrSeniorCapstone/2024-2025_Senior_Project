<template>
  <v-main>
    <v-container class="mt-5">
      <v-row>
        <v-col cols="12" md="10">
          <form @submit.prevent="submit">
            
            <h2>Study Details</h2>
            <v-text-field
              v-model="studyName"
              :counter="25"
              label="Study Name *"
              :rules="studyNameRules"
            ></v-text-field>

            <v-text-field
              v-model="studyDescription"
              :counter="250"
              label="Study Description"
              :rules="studyDescriptionRules"
            ></v-text-field>
            
            <div class="flex-row">
              <v-select
                v-model="studyDesignType"
                :items="['Between', 'Within']"
                label="Study Design Type *"
                :rules="studyDesignTypeRules"
              ></v-select>

              <v-text-field
                v-model="participantCount"
                type="number"
                label="Expected # of Participants *"
                :rules="participantCountRules"
              ></v-text-field>
            </div>

            <h3>Tasks</h3>
            <v-expansion-panels multiple>
              <v-expansion-panel v-for="(task,index) in tasks" :key="index">
                <v-expansion-panel-title>
                  <template v-slot:default= "{ }">
                    <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                      <span>{{ 'Task ' + (index+1) + ': ' + task.taskName }}</span>
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
                  <Task
                    ref = "taskRefs"
                    :task="task"
                    @remove="() => removeTask(index)"
                  />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>

            <v-container>
              <v-btn @click="addTask" color="grey" class="add-btn">
                <v-icon left>mdi-plus</v-icon>
                Add Task
              </v-btn>
            </v-container>

            <h3>Factors</h3>
            <v-expansion-panels multiple>
              <v-expansion-panel v-for="(factor,index) in factors" :key="index">
                <v-expansion-panel-title>
                  <template v-slot:default= "{ }">
                    <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                      <span>{{ 'Factor ' + (index+1) + ': ' + factor.factorName }}</span>
                      <div class="move-arrows">
                        <v-btn icon @click.stop="slideFactorUp(index)" :disabled="index === 0" size="x-small" class="individual-arrow">
                          <v-icon icon="mdi-arrow-up" size="x-small"></v-icon>
                        </v-btn>
                        <v-btn icon @click.stop="slideFactorDown(index)" :disabled="index === factors.length - 1" size="x-small" class="individual-arrow">
                          <v-icon icon="mdi-arrow-down" size="x-small"></v-icon>
                        </v-btn>
                      </div>
                    </div>
                  </template>
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <Factor
                      ref="factorRefs"
                      :factor="factor"
                      @remove="() => removeFactor(index)"
                  />
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
            
            <v-container>
              <v-btn @click="addFactor" color="grey" class="add-btn">
                <v-icon left>mdi-plus</v-icon>
                Add Factor
              </v-btn>
            </v-container>

            <v-row class="btn-row">
              <v-btn class="me-4 btn-exit" @click="exit">Exit</v-btn>
              <v-btn class="me-4 btn-submit" type="submit" :disabled="!isFormValid">Save</v-btn>
            </v-row>

          </form>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>
  
<script>
  import Task from '../components/Task.vue'
  import Factor from '../components/Factor.vue'
  import axios from 'axios'
  import { useRouter } from 'vue-router'
  import { ref } from 'vue'

  export default {
    components: { Task, Factor },

    setup() {
      const router = useRouter();
      const exit = () => {
        router.go(-1);
      };
      const factorRefs = ref([]);
      const taskRefs = ref([]);
      const validateFactors = () => {
        return factorRefs.value.every(factorRef => factorRef?.validateFactorFields());
      }
      const validateTasks = () => {
        return taskRefs.value.every(taskRef => taskRef?.validateTaskFields());
      }
      return { exit, factorRefs, validateFactors, taskRefs, validateTasks };
    },

    data() {
      return {
        studyName: '',
        studyDescription: '',
        studyDesignType: null,
        participantCount: '',
        tasks: [],
        factors: [],
        studyNameRules: [
          v => !!v || 'Study name is required.',
          v => v.length >= 2 || 'Study name must be at least 2 characters.',
          v => v.length <= 25 || 'Study name must be less than 25 characters.'
        ],
        studyDescriptionRules: [
          v => v.length <= 250 || 'Study description must be less than 250 characters.'
        ],
        studyDesignTypeRules: [
          v=> !!v || 'Must choose a study design type.'
        ],
        participantCountRules: [
          v=> v > 0 || 'Need at least 1 participant.'
        ]
      };
    },

    computed: {
      isFormValid() {
        const studyNameCheck = this.studyNameRules.every(rule => rule(this.studyName) === true);
        const studyDescCheck = this.studyDescriptionRules.every(rule => rule(this.studyDescription) === true);
        const studyDesignCheck = this.studyDesignTypeRules.every(rule => rule(this.studyDesignType) === true);
        const pCountCheck = this.participantCountRules.every(rule => rule(this.participantCount) === true);
        if(this.tasks.length === 0 || this.factors.length === 0) return false;
        const tasksCheck = this.validateTasks();
        const factorsCheck = this.validateFactors();

        return studyNameCheck && studyDescCheck && tasksCheck && factorsCheck && studyDesignCheck && pCountCheck;
      }
    },

    methods: {

      addTask() {
        this.tasks.push({
          taskName: '',
          taskDescription: '',
          taskDuration: '',
          measurementOptions: []
        });
      },

      removeTask(index) { 
        this.tasks.splice(index, 1);
      },

      slideTaskDown(index) {
        if(index < this.tasks.length - 1){
          const tempTask = this.tasks[index];
          this.tasks[index] = this.tasks[index + 1];
          this.tasks[index + 1] = tempTask;    
        }
      },

      slideTaskUp(index) {
        if(index > 0){
          const tempTask = this.tasks[index];
          this.tasks[index] = this.tasks[index - 1];
          this.tasks[index - 1] = tempTask;    
        }
      },

      addFactor() {
        this.factors.push({
          factorName: '',
          factorDescription: ''
        });
      },

      removeFactor(index) { 
        this.factors.splice(index, 1);
      },

      slideFactorDown(index) {
        if(index < this.factors.length - 1){
          const tempFactor = this.factors[index];
          this.factors[index] = this.factors[index + 1];
          this.factors[index + 1] = tempFactor;    
        }
      },

      slideFactorUp(index) {
        if(index > 0){
          const tempFactor = this.factors[index];
          this.factors[index] = this.factors[index - 1];
          this.factors[index - 1] = tempFactor;    
        }
      },

      async submit() {
        const submissionData = {
          studyName: this.studyName,
          studyDescription: this.studyDescription,
          studyDesignType: this.studyDesignType,
          participantCount: this.participantCount,
          tasks: this.tasks.map(task => ({
            taskName: task.taskName,
            taskDescription: task.taskDescription,
            taskDuration: task.taskDuration,
            measurementOptions: [...task.measurementOptions]
          })),
          factors: this.factors.map(factor => ({
            factorName: factor.factorName,
            factorDescription: factor.factorDescription
          }
          )),
        };
        
        alert(JSON.stringify(submissionData, null, 2));

        try {
          const response = await axios.post('http://localhost:5000/start_tracking', submissionData);
          console.log('Response:', response.data);
        } catch (error) {
          console.error("Error: ", error)
        }
      },
    },
  }; 
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
  .add-btn {
    max-height: 22px;
    min-width: 150px;
  }
  .flex-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
  }
</style>