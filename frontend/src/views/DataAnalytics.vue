<template>
  <div class="analytics-container">
    <h1 class="analytics-title">Data Analytics Dashboard</h1>
    
    <!-- Study selection dropdown with refresh button -->
    <div class="study-selector-container">
      <study-selector
        v-model="selectedStudyId"
        :studies="studies"
        :loading="studiesLoading"
        :error-message="studiesError"
        @refresh="fetchStudies"
        @change="handleStudyChange"
      />
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <p class="mt-4">Loading analytics data...</p>
    </div>

    <!-- Error state with retry button -->
    <div v-else-if="error" class="error-state">
      <v-alert type="error" prominent>
        <h3 class="mb-2">Error loading data</h3>
        <p>{{ error }}</p>
        <v-btn color="white" text @click="fetchData">Retry</v-btn>
      </v-alert>
    </div>

    <!-- Main dashboard content -->
    <div v-else class="dashboard">
      <!-- Summary metrics cards -->
      <div class="summary-grid">
        <dashboard-summary-card 
          v-for="metric in summaryData.metrics" 
          :key="metric.title"
          :title="metric.title"
          :value="getMetricValue(metric)"
          :change="metric.change"
          :description="metric.title"
          :format="getFormatForMetric(metric.title)"
        />
      </div>
      
      <!-- Charts section with learning curve and performance comparison -->
      <div class="charts-grid mt-6">
        <learning-curve-chart
          :data="learningCurveData"
          :loading="chartsLoading"
          :error="chartsError"
        />
        
        <task-performance-comparison
          :data="taskPerformanceData"
          :loading="chartsLoading"
          :error="chartsError"
        />
      </div>
      
      <!-- Participants data table -->
      <div class="participant-section mt-6">
        <participant-table
          :participants="participantData"
          :loading="participantsLoading"
          :error="participantsError"
        />
      </div>
    </div>
  </div>
</template>

<script>
import StudySelector from '@/components/analytics/StudySelector.vue';
import DashboardSummaryCard from '@/components/analytics/DashboardSummaryCard.vue';
import LearningCurveChart from '@/components/analytics/LearningCurveChart.vue';
import TaskPerformanceComparison from '@/components/analytics/TaskPerformanceComparison.vue';
import ParticipantTable from '@/components/analytics/ParticipantTable.vue';

export default {
  name: 'DataAnalytics',
  components: {
    StudySelector,
    DashboardSummaryCard,
    LearningCurveChart,
    TaskPerformanceComparison,
    ParticipantTable
  },
  data() {
    return {
      // Study selection data
      studies: [],
      selectedStudyId: null,
      studiesLoading: false,
      studiesError: null,

      // Overall dashboard state
      loading: true,
      error: null,
      
      // Summary metrics data
      summaryData: {
        participantCount: 0,
        avgCompletionTime: 0,
        successRate: 0,
        taskCount: 0,
        avgErrorCount: 0,
        metrics: []
      },
      
      // Charts data states
      chartsLoading: false,
      chartsError: null,
      learningCurveData: [],
      taskPerformanceData: [],
      
      // Participant table data
      participantsLoading: false,
      participantsError: null,
      participantData: []
    };
  },
  mounted() {
    // Load studies when component mounts
    this.fetchStudies();
  },
  methods: {
    // Determine the format for different metric types
    getFormatForMetric(title) {
      switch(title) {
        case 'Avg Completion Time':
          return 'time';
        case 'Success Rate':
          return 'percent';
        case 'Avg Error Count':
          return 'decimal';
        default:
          return 'number';
      }
    },
    
    // Extract numeric value from metrics that might contain units
    getMetricValue(metric) {
      if (typeof metric.value === 'string') {
        // Extract numbers from strings like "2490.24s" or "85%"
        return parseFloat(metric.value.replace(/[^\d.-]/g, ''));
      }
      return metric.value;
    },
    
    // Fetch available studies for the dropdown
    async fetchStudies() {
      this.studiesLoading = true;
      this.studiesError = null;

      try {
        const response = await fetch('http://localhost:5000/api/studies');
        
        if (!response.ok) {
          throw new Error(`Studies fetch failed: ${response.status}`);
        }
        
        this.studies = await response.json();
        
        console.group('Studies Diagnostic');
        console.log('Available Studies:', this.studies);
        console.groupEnd();
        
        // Auto-select first study if available
        if (this.studies.length > 0) {
          this.selectedStudyId = this.studies[0].id;
          this.fetchData();
        } else {
          throw new Error('No studies available');
        }
      } catch (error) {
        console.error('Error fetching studies:', error);
        this.studiesError = error.message;
      } finally {
        this.studiesLoading = false;
      }
    },

    // Handle study selection change
    handleStudyChange(studyId) {
      this.selectedStudyId = studyId;
      this.fetchData();
    },

    // Load all data for the dashboard
    async fetchData() {
      if (!this.selectedStudyId) return;
      
      this.loading = true;
      this.error = null;
      
      try {
        // Load all data types in parallel
        await Promise.all([
          this.fetchSummaryData(),
          this.fetchChartData(),
          this.fetchParticipantData()
        ]);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        this.error = error.message || 'Failed to load analytics data';
      } finally {
        this.loading = false;
      }
    },

    // Fetch summary metrics for the cards
    async fetchSummaryData() {
      try {
        const summaryResponse = await fetch(`http://localhost:5000/api/analytics/summary?study_id=${this.selectedStudyId}`);
        
        if (!summaryResponse.ok) {
          const errorText = await summaryResponse.text();
          console.error('Summary Response Error:', errorText);
          throw new Error(`Failed to fetch summary: ${summaryResponse.status} - ${errorText}`);
        }
        
        const data = await summaryResponse.json();
        
        // Process the metrics to standardize format
        if (data.metrics && Array.isArray(data.metrics)) {
          data.metrics = data.metrics.map(metric => {
            // Handle time values with 's' suffix
            if (metric.title === 'Avg Completion Time' && typeof metric.value === 'string' && metric.value.endsWith('s')) {
              const numValue = parseFloat(metric.value.slice(0, -1));
              return { ...metric, value: numValue };
            }
            // Handle percentage values with '%' suffix
            if (metric.title === 'Success Rate' && typeof metric.value === 'string' && metric.value.endsWith('%')) {
              const numValue = parseFloat(metric.value.slice(0, -1));
              return { ...metric, value: numValue };
            }
            return metric;
          });
        }
        
        this.summaryData = data;
        
        console.group('Summary Data Diagnostic');
        console.log('Processed Summary Data:', JSON.stringify(this.summaryData, null, 2));
        console.groupEnd();
      } catch (error) {
        console.error('Error fetching summary data:', error);
        throw error;
      }
    },

    // Fetch data for both charts
    async fetchChartData() {
      this.chartsLoading = true;
      this.chartsError = null;
      
      try {
        // Get learning curve data
        const learningCurveResponse = await fetch(`http://localhost:5000/api/analytics/learning-curve?study_id=${this.selectedStudyId}`);
        
        if (!learningCurveResponse.ok) {
          throw new Error(`Learning curve data request failed: ${learningCurveResponse.status}`);
        }
        
        this.learningCurveData = await learningCurveResponse.json();
        
        // Get task performance comparison data
        const taskPerformanceResponse = await fetch(`http://localhost:5000/api/analytics/task-comparison?study_id=${this.selectedStudyId}`);
        
        if (!taskPerformanceResponse.ok) {
          throw new Error(`Task performance data request failed: ${taskPerformanceResponse.status}`);
        }
        
        this.taskPerformanceData = await taskPerformanceResponse.json();
      } catch (error) {
        console.error('Error fetching chart data:', error);
        this.chartsError = error.message;
      } finally {
        this.chartsLoading = false;
      }
    },

    // Fetch participant table data
    async fetchParticipantData() {
      this.participantsLoading = true;
      this.participantsError = null;
      
      try {
        const response = await fetch(`http://localhost:5000/api/analytics/${this.selectedStudyId}/participants`);
        
        if (!response.ok) {
          throw new Error(`Participant data request failed: ${response.status}`);
        }
        
        this.participantData = await response.json();
      } catch (error) {
        console.error('Error fetching participant data:', error);
        this.participantsError = error.message;
      } finally {
        this.participantsLoading = false;
      }
    }
  }
};
</script>

<style scoped>
.analytics-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.analytics-title {
  color: #2c3e50;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 500;
}

.study-selector-container {
  margin-bottom: 24px;
}

.loading-state, .error-state {
  text-align: center;
  padding: 50px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.error-state {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 992px) {
  .charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>