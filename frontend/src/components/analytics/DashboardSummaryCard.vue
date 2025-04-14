<template>
  <v-row>
    <v-col v-for="(metric, index) in metrics" :key="index" cols="12" sm="6" md="3">
      <v-card class="summary-card" :class="getCardColorClass(metric.title)">
        <div class="d-flex align-center px-4 pt-4">
          <div class="icon-container" :class="getIconColorClass(metric.title)">
            <v-icon>{{ getIconForTitle(metric.title) }}</v-icon>
          </div>
          <div class="ms-3 flex-grow-1">
            <div class="d-flex justify-space-between align-center">
              <span class="text-subtitle-2 font-weight-medium">{{ metric.title }}</span>
              <v-chip
                v-if="metric.change !== undefined"
                size="x-small"
                :color="getChangeColor(metric.change, metric.title === 'Avg Error Count')"
                variant="outlined"
                class="ms-2"
              >
                <v-icon 
                  size="x-small" 
                  start
                  :icon="getChangeIcon(metric.change, metric.title === 'Avg Error Count')"
                ></v-icon>
                {{ formatChange(metric.change) }}
              </v-chip>
            </div>
          </div>
        </div>
        
        <v-card-text>
          <div :class="getValueColorClass(metric.title)" class="metric-value text-h4 font-weight-bold">
            {{ formatValue(metric.value, metric.title) }}
          </div>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useAnalyticsStore } from '@/stores/analyticsStore';

export default {
  name: 'DashboardSummaryCard',
  props: {
    studyId: {
      type: [Number, String],
      required: true
    }
  },
  
  setup(props) {
    const analyticsStore = useAnalyticsStore();
    const loading = ref(false);
    const error = ref(false);
    
    // Load data when component mounts or studyId changes
    watch(() => props.studyId, (newId) => {
      if (newId) {
        loadData(newId);
      }
    }, { immediate: true });
    
    const loadData = async (studyId) => {
      loading.value = true;
      error.value = false;
      
      try {
        await analyticsStore.fetchSummaryMetrics(studyId);
        loading.value = false;
      } catch (err) {
        console.error('Error loading summary metrics:', err);
        loading.value = false;
        error.value = true;
      }
    };
    
    // Get metrics from store
    const metrics = computed(() => {
      const summaryData = analyticsStore.getSummaryMetrics;
      return summaryData.metrics || [];
    });
    
    // Format the value based on metric title
    const formatValue = (value, title) => {
      if (value === undefined || value === null) return '–';
      
      if (title === 'Success Rate') {
        return typeof value === 'string' ? value : `${value.toFixed(1)}%`;
      } else if (title === 'Avg Completion Time') {
        return typeof value === 'string' ? value : `${value.toFixed(2)}s`;
      } else {
        return value;
      }
    };
    
    // Format the change percentage
    const formatChange = (change) => {
      if (change === undefined || change === null) return '';
      return `${Math.abs(change).toFixed(1)}%`;
    };
    
    // Get the appropriate icon for the change
    const getChangeIcon = (change, invertLogic = false) => {
      if (change === 0) return 'mdi-minus';
      
      const isPositive = change > 0;
      const isGood = invertLogic ? !isPositive : isPositive;
      
      return isGood ? 'mdi-arrow-up' : 'mdi-arrow-down';
    };
    
    // Get the appropriate color for the change
    const getChangeColor = (change, invertLogic = false) => {
      if (change === 0) return 'grey';
      
      const isPositive = change > 0;
      const isGood = invertLogic ? !isPositive : isPositive;
      
      return isGood ? 'success' : 'error';
    };
    
    // Get icon based on metric title
    const getIconForTitle = (title) => {
      const icons = {
        'Participants': 'mdi-account-group',
        'Avg Completion Time': 'mdi-clock-outline',
        'Success Rate': 'mdi-check-circle-outline',
        'Avg Error Count': 'mdi-alert-circle-outline'
      };
      return icons[title] || 'mdi-chart-box';
    };
    
    // Get card color class based on title
    const getCardColorClass = (title) => {
      switch (title) {
        case 'Participants': return 'card-participants';
        case 'Avg Completion Time': return 'card-time';
        case 'Success Rate': return 'card-success';
        case 'Avg Error Count': return 'card-error';
        default: return '';
      }
    };
    
    // Get icon color class based on title
    const getIconColorClass = (title) => {
      switch (title) {
        case 'Participants': return 'icon-participants';
        case 'Avg Completion Time': return 'icon-time';
        case 'Success Rate': return 'icon-success';
        case 'Avg Error Count': return 'icon-error';
        default: return '';
      }
    };
    
    // Get value color class based on title
    const getValueColorClass = (title) => {
      switch (title) {
        case 'Participants': return 'value-participants';
        case 'Avg Completion Time': return 'value-time';
        case 'Success Rate': return 'value-success';
        case 'Avg Error Count': return 'value-error';
        default: return '';
      }
    };
    
    return {
      metrics,
      loading,
      error,
      formatValue,
      formatChange,
      getChangeIcon,
      getChangeColor,
      getIconForTitle,
      getCardColorClass,
      getIconColorClass,
      getValueColorClass
    };
  }
};
</script>

<style scoped>
.summary-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  overflow: hidden;
}

.summary-card:hover {
  transform: translateY(-5px);
}

.icon-container {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.metric-value {
  font-size: 24px;
  margin-top: 8px;
}

/* Card theme colors */
.card-participants {
  border-top: 3px solid #1976D2;
}

.card-time {
  border-top: 3px solid #4CAF50;
}

.card-success {
  border-top: 3px solid #2196F3;
}

.card-error {
  border-top: 3px solid #F44336;
}

/* Icon theme colors */
.icon-participants {
  background-color: rgba(25, 118, 210, 0.15);
  color: #1976D2;
}

.icon-time {
  background-color: rgba(76, 175, 80, 0.15);
  color: #4CAF50;
}

.icon-success {
  background-color: rgba(33, 150, 243, 0.15);
  color: #2196F3;
}

.icon-error {
  background-color: rgba(244, 67, 54, 0.15);
  color: #F44336;
}

/* Value theme colors */
.value-participants {
  color: #1976D2;
}

.value-time {
  color: #4CAF50;
}

.value-success {
  color: #2196F3;
}

.value-error {
  color: #F44336;
}
</style>