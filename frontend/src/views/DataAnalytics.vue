<template>
  <div class="analytics-container">
    <h1>Data Analytics Dashboard</h1>
    
    <div v-if="loading" class="loading-state">
      Loading analytics data...
    </div>
    
    <div v-else-if="error" class="error-state">
      <h3>Error loading data</h3>
      <p>{{ error }}</p>
      <button @click="fetchData" class="retry-button">Retry</button>
    </div>
    
    <div v-else class="dashboard">
      <div class="summary-section">
        <h2>Summary</h2>
        <pre>{{ JSON.stringify(summaryData, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataAnalytics',
  data() {
    return {
      loading: true,
      error: null,
      summaryData: null
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      this.error = null;
      
      try {
        // First test if the backend is accessible
        const healthResponse = await fetch('http://localhost:5000/api/health');
        if (!healthResponse.ok) {
          throw new Error(`Backend health check failed: ${healthResponse.status}`);
        }
        
        // Try to get summary data
        const summaryResponse = await fetch('http://localhost:5000/api/analytics/summary');
        if (!summaryResponse.ok) {
          throw new Error(`Failed to fetch summary data: ${summaryResponse.status}`);
        }
        
        this.summaryData = await summaryResponse.json();
        this.loading = false;
      } catch (error) {
        console.error('Error fetching analytics data:', error);
        this.error = error.message;
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.analytics-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 30px;
}

.loading-state, .error-state {
  text-align: center;
  padding: 50px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin: 20px 0;
}

.error-state {
  color: #721c24;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.retry-button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 15px;
}

.summary-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

pre {
  white-space: pre-wrap;
  background-color: #e9ecef;
  padding: 15px;
  border-radius: 4px;
  overflow: auto;
}
</style>