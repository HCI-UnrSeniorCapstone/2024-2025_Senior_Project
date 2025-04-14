import axios from 'axios';

// Always use the proxy for analytics API
const API_BASE_URL = '/api';

// Cache configuration
const CACHE_TTL = 60000; // 1 minute cache lifetime in milliseconds
const cache = new Map();

// Get API client with the right baseURL
// baseUrl - URL for API requests
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

// Handle API errors
// error - The error that occurred
// operation - What failed
const handleApiError = (error, operation) => {
  const errorMessage = error.response?.data?.error || error.message || 'Unknown error';
  console.error(`Analytics API error (${operation}): ${errorMessage}`, error);
  throw error;
};

// Get cached data or fetch fresh data
// key - Cache key
// fetchFn - Function to get fresh data
const getCachedData = async (key, fetchFn) => {
  const now = Date.now();
  const cachedItem = cache.get(key);
  
  // Return cached data if valid
  if (cachedItem && now - cachedItem.timestamp < CACHE_TTL) {
    return cachedItem.data;
  }
  
  // Fetch fresh data
  const data = await fetchFn();
  
  // Cache the result
  cache.set(key, { data, timestamp: now });
  return data;
};

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
  
  // Clear cache when URL changes
  cache.clear();
};

const analyticsApi = {
  // Configuration
  setBackendUrl,
  
  // Study related endpoints
  async getStudies() {
    return getCachedData('studies', async () => {
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
        handleApiError(error, 'getStudies');
      }
    });
  },

  // Summary metrics endpoint
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
      handleApiError(error, `getSummaryMetrics(${studyId})`);
    }
  },

  // Learning curve data endpoint
  async getLearningCurveData(studyId) {
    try {
      let client = apiClient;
      let endpoint = `/analytics/${studyId}/learning-curve`;
      
      // Use custom backend URL if set
      if (customBackendUrl) {
        client = getApiClient(customBackendUrl);
        endpoint = `/api/analytics/${studyId}/learning-curve`;
      }
      
      const response = await client.get(endpoint);
      return response.data;
    } catch (error) {
      handleApiError(error, `getLearningCurveData(${studyId})`);
    }
  },

  // Task performance endpoint
  async getTaskPerformanceData(studyId) {
    try {
      let client = apiClient;
      let endpoint = `/analytics/${studyId}/task-performance`;
      
      // Use custom backend URL if set
      if (customBackendUrl) {
        client = getApiClient(customBackendUrl);
        endpoint = `/api/analytics/${studyId}/task-performance`;
      }
      
      const response = await client.get(endpoint);
      return response.data;
    } catch (error) {
      handleApiError(error, `getTaskPerformanceData(${studyId})`);
    }
  },

  // Participant data endpoint
  async getParticipantData(studyId, page = 1, pageSize = 20) {
    try {
      let client = apiClient;
      let endpoint = `/analytics/${studyId}/participants`;
      
      // Use custom backend URL if set
      if (customBackendUrl) {
        client = getApiClient(customBackendUrl);
        endpoint = `/api/analytics/${studyId}/participants`;
      }
      
      const response = await client.get(endpoint, {
        params: { page, pageSize }
      });
      return response.data;
    } catch (error) {
      handleApiError(error, `getParticipantData(${studyId})`);
    }
  },

  // Health check endpoint
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
      handleApiError(error, 'healthCheck');
    }
  },

  // Data export endpoint
  async exportStudyData(studyId, format = 'csv') {
    try {
      // Validate format
      if (!['csv', 'json', 'xlsx'].includes(format)) {
        throw new Error(`Unsupported export format: ${format}. Must be csv, json, or xlsx.`);
      }
      
      let baseUrl = API_BASE_URL;
      
      // Use custom backend URL if set
      if (customBackendUrl) {
        baseUrl = customBackendUrl;
      }
      
      const response = await axios.get(
        `${baseUrl}/analytics/${studyId}/export`,
        {
          params: { format },
          responseType: 'blob' // Important for file exports
        }
      );
      return response.data;
    } catch (error) {
      handleApiError(error, `exportStudyData(${studyId}, ${format})`);
    }
  }
};

export default analyticsApi;