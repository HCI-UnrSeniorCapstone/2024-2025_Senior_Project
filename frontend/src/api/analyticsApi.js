import axios from 'axios';

// Always use the proxy for analytics API
const API_BASE_URL = '/api';

// Create a function to get the API client with the correct baseURL
function getApiClient(baseUrl = API_BASE_URL) {
  return axios.create({
    baseURL: baseUrl,
    timeout: 15000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  });
}

// Default client using the proxy
const apiClient = getApiClient();

// Request interceptor for API calls
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Analytics API Request: ${config.method} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('API request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for API calls
apiClient.interceptors.response.use(
  (response) => {
    console.log(`Analytics API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API response error:', error.response || error.message);
    return Promise.reject(error);
  }
);

// Function to set a custom backend URL (can be called from components)
let customBackendUrl = null;
const setBackendUrl = (url) => {
  customBackendUrl = url;
  console.log('Analytics API using custom backend URL:', customBackendUrl);
};

const analyticsApi = {
  // Allow setting the backend URL from components
  setBackendUrl,
  
  // Fetch all the studies 
  async getStudies() {
    try {
      let client = apiClient;
      let endpoint = '/analytics/studies';
      
      // Use custom backend URL if set
      if (customBackendUrl) {
        client = getApiClient(customBackendUrl);
        endpoint = '/api/analytics/studies';
      }
      
      const response = await client.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch studies:', error);
      throw error;
    }
  },

  // Get summary data for a specific study
  // studyId is the unique identifier for the study
  async getSummaryMetrics(studyId) {
    try {
      let client = apiClient;
      let endpoint = `/analytics/${studyId}/summary`;
      
      // Use custom backend URL if set
      if (customBackendUrl) {
        client = getApiClient(customBackendUrl);
        endpoint = `/api/analytics/${studyId}/summary`;
      }
      
      const response = await client.get(endpoint);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch summary metrics for study ${studyId}:`, error);
      throw error;
    }
  },

  
  // Get learning curve info for a study
  // studyId is the ID of the study you're interested in
  async getLearningCurveData(studyId) {
    try {
      const response = await apiClient.get(`/analytics/${studyId}/learning-curve`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch learning curve data for study ${studyId}:`, error);
      throw error;
    }
  },

  
  // Get task performance data for a study
  // studyId again is needed here
  async getTaskPerformanceData(studyId) {
    try {
      const response = await apiClient.get(`/analytics/${studyId}/task-performance`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch task performance data for study ${studyId}:`, error);
      throw error;
    }
  },

  
  // Get participant data for a specific study
  // This includes all participants involved in the study
  async getParticipantData(studyId) {
    try {
      const response = await apiClient.get(`/analytics/${studyId}/participants`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch participant data for study ${studyId}:`, error);
      throw error;
    }
  },

  // Health check endpoint for testing connectivity
  async healthCheck() {
    try {
      let client = apiClient;
      let endpoint = '/analytics/health';
      
      // Use custom backend URL if set
      if (customBackendUrl) {
        client = getApiClient(customBackendUrl);
        endpoint = '/api/analytics/health';
      }
      
      const response = await client.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  
  // Export study data to the format you want (csv, json)
  // Default is csv, but you can choose json too
  async exportStudyData(studyId, format = 'csv') {
    const response = await axios.get(
      `${API_BASE_URL}/analytics/${studyId}/export`,
      {
        params: { format },
        responseType: 'blob' // Important for file exports
      }
    );
    return response.data;
  }
};

export default analyticsApi;