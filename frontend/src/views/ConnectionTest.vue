<template>
  <div class="connection-test">
    <h1>Server Connection Test</h1>
    
    <v-card class="mb-4 pa-4">
      <h2>Server Configuration</h2>
      <p><strong>Backend URL:</strong> {{ backendUrl }}</p>
      <p><strong>API Proxy:</strong> <code>/api</code> → <code>{{ apiProxyTarget }}</code></p>
      
      <div class="d-flex justify-space-between mt-4">
        <v-btn color="primary" @click="runAllTests">
          Run All Tests
        </v-btn>
        <v-btn @click="clearResults">
          Clear Results
        </v-btn>
      </div>
    </v-card>
    
    <div class="test-buttons mb-4">
      <v-btn class="mr-2" @click="testDirectConnection">Test Direct Connection</v-btn>
      <v-btn class="mr-2" @click="testProxyConnection">Test Proxy Connection</v-btn>
      <v-btn class="mr-2" @click="testAnalyticsHealth">Test Analytics Health</v-btn>
      <v-btn @click="testStudiesList">Test Studies List</v-btn>
    </div>
    
    <v-card v-if="loadingTest" class="mb-4 pa-4">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
      <p class="mt-2">Running test...</p>
    </v-card>
    
    <template v-if="testResults.length > 0">
      <h2>Test Results</h2>
      <v-card v-for="(result, index) in testResults" :key="index" class="mb-2 pa-4" :color="getResultColor(result.success)">
        <h3>{{ result.title }}</h3>
        <p><strong>Status:</strong> {{ result.success ? 'Success' : 'Failed' }}</p>
        <div v-if="result.details" class="mt-2">
          <p><strong>Details:</strong></p>
          <pre>{{ JSON.stringify(result.details, null, 2) }}</pre>
        </div>
        <div v-if="result.error" class="mt-2 error--text">
          <p><strong>Error:</strong></p>
          <pre>{{ result.error }}</pre>
        </div>
      </v-card>
    </template>
    
    <h2 v-if="recommendations.length > 0" class="mt-4">Recommendations</h2>
    <v-card v-if="recommendations.length > 0" class="pa-4">
      <ul>
        <li v-for="(rec, index) in recommendations" :key="index" class="mb-2">
          {{ rec }}
        </li>
      </ul>
    </v-card>
  </div>
</template>

<script>
import axios from 'axios';
import { testDirectConnection, testProxyConnection, tryBothUrls } from '@/api/debugHelper';
import analyticsApi from '@/api/analyticsApi';

export default {
  data() {
    return {
      backendUrl: '',
      apiProxyTarget: 'http://100.82.85.28:5004',
      testResults: [],
      loadingTest: false,
      recommendations: []
    };
  },
  mounted() {
    // Get the backend URL from global properties
    this.backendUrl = this.$backendUrl || 'Not set';
    
    // Check if we can extract from Vite env
    try {
      const viteBackendUrl = import.meta.env.VITE_BACKEND_URL;
      const viteBackendPort = import.meta.env.VITE_BACKEND_PORT;
      
      if (viteBackendUrl && viteBackendPort) {
        console.log(`Detected from Vite env: ${viteBackendUrl}:${viteBackendPort}`);
      }
    } catch (e) {
      console.log('No Vite env variables detected');
    }
  },
  methods: {
    async runAllTests() {
      this.clearResults();
      await this.testDirectConnection();
      await this.testProxyConnection();
      await this.testAnalyticsHealth();
      await this.testStudiesList();
      this.generateRecommendations();
    },
    
    clearResults() {
      this.testResults = [];
      this.recommendations = [];
    },
    
    getResultColor(success) {
      return success ? 'light-green lighten-4' : 'red lighten-4';
    },
    
    async testDirectConnection() {
      this.loadingTest = true;
      try {
        const result = await testDirectConnection(this.backendUrl);
        this.testResults.push({
          title: 'Direct Backend Connection',
          success: result.success,
          details: result.data,
          error: result.error
        });
      } catch (error) {
        this.testResults.push({
          title: 'Direct Backend Connection',
          success: false,
          error: error.message
        });
      } finally {
        this.loadingTest = false;
      }
    },
    
    async testProxyConnection() {
      this.loadingTest = true;
      try {
        const result = await testProxyConnection();
        this.testResults.push({
          title: 'Proxy API Connection',
          success: result.success,
          details: result.data,
          error: result.error
        });
      } catch (error) {
        this.testResults.push({
          title: 'Proxy API Connection',
          success: false,
          error: error.message
        });
      } finally {
        this.loadingTest = false;
      }
    },
    
    async testAnalyticsHealth() {
      this.loadingTest = true;
      try {
        const healthData = await analyticsApi.healthCheck();
        this.testResults.push({
          title: 'Analytics Health Check',
          success: true,
          details: healthData
        });
      } catch (error) {
        this.testResults.push({
          title: 'Analytics Health Check',
          success: false,
          error: error.message
        });
      } finally {
        this.loadingTest = false;
      }
    },
    
    async testStudiesList() {
      this.loadingTest = true;
      try {
        // First try with direct URL
        const userID = 1;
        const directUrl = `${this.backendUrl}/get_study_data/${userID}`;
        const proxyUrl = `/api/get_study_data/${userID}`;
        
        const results = await tryBothUrls(directUrl);
        
        this.testResults.push({
          title: 'Studies List API',
          success: results.direct.success || results.proxy.success,
          details: {
            directUrl,
            proxyUrl,
            directSuccess: results.direct.success,
            proxySuccess: results.proxy.success,
            data: results.direct.success ? results.direct.data : results.proxy.data
          },
          error: !results.direct.success && !results.proxy.success 
            ? `Direct: ${results.direct.error}, Proxy: ${results.proxy.error}` 
            : null
        });
      } catch (error) {
        this.testResults.push({
          title: 'Studies List API',
          success: false,
          error: error.message
        });
      } finally {
        this.loadingTest = false;
      }
    },
    
    generateRecommendations() {
      this.recommendations = [];
      
      // Check if direct connection failed but proxy worked
      const directTest = this.testResults.find(r => r.title === 'Direct Backend Connection');
      const proxyTest = this.testResults.find(r => r.title === 'Proxy API Connection');
      
      if (directTest && !directTest.success && proxyTest && proxyTest.success) {
        this.recommendations.push(
          'Direct connection failed but proxy connection worked. Consider updating all API calls to use the proxy format (/api/...).'
        );
      }
      
      if (directTest && directTest.success && proxyTest && !proxyTest.success) {
        this.recommendations.push(
          'Direct connection works but proxy connection failed. Check the proxy configuration in vite.config.js.'
        );
      }
      
      const studiesTest = this.testResults.find(r => r.title === 'Studies List API');
      if (studiesTest) {
        const details = studiesTest.details || {};
        if (details.directSuccess && !details.proxySuccess) {
          this.recommendations.push(
            'The UserStudies view should continue using direct URLs as the proxy is not configured for those endpoints.'
          );
        }
        
        if (!details.directSuccess && details.proxySuccess) {
          this.recommendations.push(
            'The UserStudies view should be updated to use the proxy URL format for API calls.'
          );
        }
      }
      
      // If we have no clear solution, suggest a comprehensive approach
      if (this.recommendations.length === 0) {
        this.recommendations.push(
          'Consider standardizing all API calls to use either direct URLs or the proxy format consistently.'
        );
        this.recommendations.push(
          'Ensure vite.config.js proxy is correctly configured to forward all relevant API paths.'
        );
      }
    }
  }
};
</script>

<style scoped>
.connection-test {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow: auto;
  max-height: 300px;
}

.test-buttons {
  margin-bottom: 20px;
}
</style>