<template>
  <v-card class="custom-formula-card">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-function-variant" class="me-2"></v-icon>
      Custom Formula
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-icon small class="ml-2" v-bind="attrs" v-on="on">
            mdi-information-outline
          </v-icon>
        </template>
        <span>Create a custom formula to analyze your data</span>
      </v-tooltip>
    </v-card-title>
    <v-divider></v-divider>
    
    <v-card-text>
      <v-row>
        <v-col cols="12">
          <v-text-field
            v-model="formulaName"
            label="Formula Name"
            placeholder="e.g., Efficiency Index"
            outlined
            dense
          ></v-text-field>
        </v-col>
        
        <v-col cols="12">
          <v-textarea
            v-model="formulaExpression"
            label="Formula Expression"
            placeholder="e.g., (completionTime / 60) * (1 - errorRate)"
            outlined
            rows="3"
            :error-messages="formulaError"
            @input="validateFormula"
          ></v-textarea>
          
          <v-alert
            v-if="isFormulaValid && !formulaError"
            type="success"
            dense
            class="mt-2"
          >
            Formula looks valid
          </v-alert>
        </v-col>
      </v-row>
      
      <div class="formula-help mt-2">
        <p class="text-subtitle-2 mb-2">Available Variables:</p>
        <v-chip-group>
          <v-chip small @click="insertVariable('completionTime')">completionTime</v-chip>
          <v-chip small @click="insertVariable('taskCount')">taskCount</v-chip>
          <v-chip small @click="insertVariable('pValue')">pValue</v-chip>
          <v-chip small @click="insertVariable('confidenceInterval')">confidenceInterval</v-chip>
          <v-chip small @click="insertVariable('participantCount')">participantCount</v-chip>
        </v-chip-group>
        
        <p class="text-subtitle-2 mb-2 mt-4">Examples:</p>
        <v-list dense>
          <v-list-item>
            <v-list-item-title class="text-caption">
              <code>(1 - pValue) * 100</code> - Confidence percentage
            </v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-title class="text-caption">
              <code>completionTime / taskCount</code> - Average time per task
            </v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-title class="text-caption">
              <code>Math.log(1/pValue) * completionTime</code> - Significance-weighted time
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </div>
    </v-card-text>
    
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        :disabled="!isFormulaValid || !formulaName"
        @click="applyFormula"
      >
        <v-icon left>mdi-check</v-icon>
        Apply Formula
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { ref, computed } from 'vue';
import CustomFormulaMetric from '@/api/metrics/CustomFormulaMetric';
import { useAnalyticsStore } from '@/stores/analyticsStore';

export default {
  name: 'CustomFormulaInput',
  props: {
    studyId: {
      type: [String, Number],
      required: true
    }
  },
  emits: ['formula-applied'],
  
  setup(props, { emit }) {
    const analyticsStore = useAnalyticsStore();
    const formulaName = ref('');
    const formulaExpression = ref('');
    const formulaError = ref('');
    const isFormulaValid = ref(false);
    
    // Validate the formula syntax
    const validateFormula = () => {
      if (!formulaExpression.value) {
        formulaError.value = '';
        isFormulaValid.value = false;
        return;
      }
      
      try {
        // Create a test function to validate the formula
        const testFn = new Function(
          'completionTime', 
          'taskCount', 
          'pValue', 
          'confidenceInterval', 
          'participantCount',
          `return ${formulaExpression.value};`
        );
        
        // Test the function with sample values
        testFn(120, 5, 0.05, 0.03, 10);
        
        formulaError.value = '';
        isFormulaValid.value = true;
      } catch (err) {
        formulaError.value = `Formula error: ${err.message}`;
        isFormulaValid.value = false;
      }
    };
    
    // Insert a variable into the formula at the cursor position
    const insertVariable = (variable) => {
      formulaExpression.value += variable;
      validateFormula();
    };
    
    // Create and apply the custom formula
    const applyFormula = () => {
      if (!isFormulaValid.value || !formulaName.value) return;
      
      // Create the actual formula function
      const formulaFunction = (data) => {
        if (!Array.isArray(data) || data.length === 0) {
          return { overall: 0, byTask: {} };
        }
        
        // Calculate base metrics needed for the formula
        const taskGroups = {};
        data.forEach(result => {
          const taskId = result.taskId || result.task_id;
          if (!taskGroups[taskId]) {
            taskGroups[taskId] = [];
          }
          taskGroups[taskId].push(result);
        });
        
        // Process each task
        const byTask = {};
        let overallResult = 0;
        
        Object.entries(taskGroups).forEach(([taskId, results]) => {
          const completionTimes = results.map(r => r.completionTime || r.completion_time || 0);
          const successCounts = results.filter(r => r.success || r.isSuccess).length;
          
          // Variables for the formula
          const completionTime = completionTimes.reduce((sum, t) => sum + t, 0) / 
                              (completionTimes.length || 1);
          const taskCount = taskGroups[taskId].length;
          const pValue = results[0].pValue || 0.05; // Use p-value from data or default
          const confidenceInterval = 1.96 * Math.sqrt(pValue * (1 - pValue) / taskCount);
          const participantCount = new Set(results.map(r => r.participantId || r.participant_id)).size;
          
          try {
            const formulaFn = new Function(
              'completionTime', 
              'taskCount', 
              'pValue', 
              'confidenceInterval', 
              'participantCount',
              `return ${formulaExpression.value};`
            );
            
            byTask[taskId] = formulaFn(completionTime, taskCount, pValue, confidenceInterval, participantCount);
          } catch (err) {
            console.error('Error executing formula for task', taskId, err);
            byTask[taskId] = 0;
          }
        });
        
        // Calculate the overall metric as average of task values
        const taskValues = Object.values(byTask);
        overallResult = taskValues.length > 0 
          ? taskValues.reduce((sum, val) => sum + val, 0) / taskValues.length
          : 0;
        
        return { overall: overallResult, byTask };
      };
      
      // Create a custom metric
      const customMetric = new CustomFormulaMetric({
        name: formulaName.value,
        description: `Custom metric: ${formulaExpression.value}`,
        formula: formulaFunction
      });
      
      // Register the metric with a unique key
      const metricKey = `custom_${Date.now()}`;
      analyticsStore.registerCustomMetric(metricKey, customMetric);
      
      // Apply the metric to current data
      const result = analyticsStore.calculateCustomMetric(metricKey, props.studyId);
      
      // Emit the result
      emit('formula-applied', {
        key: metricKey,
        name: formulaName.value,
        expression: formulaExpression.value,
        result
      });
      
      // Reset the form
      formulaName.value = '';
      formulaExpression.value = '';
      validateFormula();
    };
    
    return {
      formulaName,
      formulaExpression,
      formulaError,
      isFormulaValid,
      validateFormula,
      insertVariable,
      applyFormula
    };
  }
};
</script>

<style scoped>
.custom-formula-card {
  margin-bottom: 20px;
}

.formula-help {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  margin-top: 8px;
}
</style>