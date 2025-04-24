import axios from 'axios';

// Always use the proxy for analytics API
const API_BASE_URL = '/api';
const DIRECT_API_URL = 'http://localhost:5004/api';

// Cache configuration
const CACHE_TTL = 60000; // 1 minute cache lifetime in milliseconds
const cache = new Map();

// Get API client with the right baseURL
// baseUrl - URL for API requests
function getApiClient(baseUrl = API_BASE_URL) {
  return axios.create({
    baseURL: baseUrl,
    timeout: 30000, // 30 seconds timeout for larger requests
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    // Add responseType: 'json' explicitly
    responseType: 'json',
    // Add max content length option
    maxContentLength: 50 * 1024 * 1024 // 50MB max response size
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
  
  try {
    // Fetch fresh data
    const data = await fetchFn();
    
    // Cache the result
    cache.set(key, { data, timestamp: now });
    return data;
  } catch (error) {
    console.error(`Cache fetch error for key ${key}:`, error);
    throw error;
  }
};

// Default client using the proxy
const apiClient = getApiClient();
// Direct client for fallback (no proxy)
const directApiClient = getApiClient(DIRECT_API_URL);

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

// Retry API calls with exponential backoff
const retryApiCall = async (apiCall, maxRetries = 2, initialDelay = 300) => {
  let retryCount = 0;
  let delay = initialDelay;
  
  while (retryCount <= maxRetries) {
    try {
      return await apiCall();
    } catch (error) {
      // Don't retry if we've reached the max
      if (retryCount >= maxRetries) {
        throw error;
      }
      
      // Don't retry certain errors like 401, 403, 404
      if (error.response && [401, 403, 404].includes(error.response.status)) {
        throw error;
      }
      
      console.log(`Retrying API call (attempt ${retryCount + 1} of ${maxRetries})...`);
      // Wait before retrying
      await new Promise(resolve => setTimeout(resolve, delay));
      
      // Exponential backoff
      delay *= 2;
      retryCount++;
    }
  }
};

// Helper function for API calls with fallback to direct connection
const makeApiCallWithFallback = async (path, options = {}) => {
  try {
    // First try through the proxy
    try {
      return await retryApiCall(() => apiClient.get(path, options));
    } catch (proxyError) {
      console.log('API request failed through proxy, trying direct connection...', proxyError.message);
      
      // Remove leading slash if present when switching to direct connection
      const directPath = path.startsWith('/') ? path : `/${path}`;
      return await retryApiCall(() => directApiClient.get(directPath, options));
    }
  } catch (error) {
    console.error(`API call failed for ${path}:`, error.message);
    throw error;
  }
};

// Empty placeholder objects for minimal error handling
const emptyStudyData = [];

const emptySummaryMetrics = {
  "participantCount": 0,
  "avgCompletionTime": 0,
  "metrics": [
    {
      "title": "Participants",
      "value": 0,
      "icon": "mdi-account-group",
      "color": "primary"
    },
    {
      "title": "Avg Completion Time",
      "value": "0s",
      "icon": "mdi-clock-outline",
      "color": "info"
    }
  ]
};

const emptyLearningCurve = [];

const emptyTaskPerformance = [];

const emptyParticipants = {
  "data": [],
  "pagination": {
    "total": 0,
    "page": 1,
    "per_page": 20,
    "pages": 0
  }
};

const analyticsApi = {
  // Configuration
  setBackendUrl,
  
  // Study related endpoints
  async getStudies() {
    // Clear cache to ensure fresh data
    cache.delete('studies');
    
    return getCachedData('studies', async () => {
      try {
        console.log('Attempting to get studies from API...');
        
        // Normal API call
        const response = await makeApiCallWithFallback('/analytics/studies');
        console.log('Successfully got studies from API:', response.data);
        return response.data;
      } catch (error) {
        console.error('Failed to fetch studies from API:', error);
        return [...emptyStudyData];
      }
    });
  },

  // Summary metrics endpoint
  async getSummaryMetrics(studyId) {
    return getCachedData(`summary_${studyId}`, async () => {
      try {
        console.log(`Attempting to get summary metrics for study ${studyId}...`);
        
        // Try API call with fallback
        const response = await makeApiCallWithFallback(`/analytics/${studyId}/summary`);
        console.log('Successfully got summary metrics from API');
        return response.data;
      } catch (error) {
        console.log('API request failed, using empty data');
        return emptySummaryMetrics;
      }
    });
  },

  // Learning curve data endpoint
  async getLearningCurveData(studyId) {
    return getCachedData(`learning_${studyId}`, async () => {
      try {
        console.log(`Attempting to get learning curve data for study ${studyId}...`);
        
        // Try API call with fallback
        const response = await makeApiCallWithFallback(`/analytics/${studyId}/learning-curve`);
        console.log('Successfully got learning curve data from API');
        return response.data;
      } catch (error) {
        console.log('API request failed, using empty data');
        return emptyLearningCurve;
      }
    });
  },

  // Task performance endpoint
  async getTaskPerformanceData(studyId) {
    return getCachedData(`tasks_${studyId}`, async () => {
      try {
        console.log(`Attempting to get task performance data for study ${studyId}...`);
        
        // Try API call with fallback
        const response = await makeApiCallWithFallback(`/analytics/${studyId}/task-performance`);
        console.log('Successfully got task performance data from API');
        return response.data;
      } catch (error) {
        console.log('API request failed, using empty data');
        return emptyTaskPerformance;
      }
    });
  },

  // Participant data endpoint
  async getParticipantData(studyId, page = 1, pageSize = 20) {
    return getCachedData(`participants_${studyId}_${page}_${pageSize}`, async () => {
      try {
        console.log(`Attempting to get participant data for study ${studyId}...`);
        
        // Try API call with fallback
        const response = await makeApiCallWithFallback(`/analytics/${studyId}/participants`, {
          params: { page, pageSize }
        });
        console.log('Successfully got participant data from API');
        return response.data;
      } catch (error) {
        console.log('API request failed, using empty data');
        return emptyParticipants;
      }
    });
  },

  // Health check endpoint
  async healthCheck() {
    try {
      console.log('Attempting health check...');
      
      // Try API call with fallback
      const response = await makeApiCallWithFallback('/analytics/health');
      console.log('Health check successful');
      return response.data;
    } catch (error) {
      console.error('Health check failed, returning empty status:', error);
      return {
        "status": "error", 
        "mode": "empty",
        "message": "API connection failed, no data available"
      };
    }
  },

  // Data export endpoint
  async exportStudyData(studyId, format = 'csv') {
    try {
      // Validate format
      if (!['csv', 'json', 'xlsx'].includes(format)) {
        throw new Error(`Unsupported export format: ${format}. Must be csv, json, or xlsx.`);
      }
      
      console.log(`Attempting to export study data for study ${studyId} in ${format} format...`);
      
      try {
        // For file downloads, we need different response type
        const options = {
          params: { format },
          responseType: 'blob'
        };
        
        // Try API call with fallback (custom handling for blob responses)
        try {
          const response = await apiClient.get(`/analytics/${studyId}/export`, options);
          console.log('Export successful via proxy');
          return response.data;
        } catch (proxyError) {
          console.log('Export via proxy failed, trying direct connection...');
          const response = await directApiClient.get(`/analytics/${studyId}/export`, options);
          console.log('Export successful via direct connection');
          return response.data;
        }
      } catch (error) {
        console.error(`Export failed:`, error);
        throw error;
      }
    } catch (error) {
      console.error(`Failed to export study data for study ${studyId}:`, error);
      handleApiError(error, `exportStudyData(${studyId}, ${format})`);
    }
  },

  // NEW METHODS FOR ZIP DATA ANALYTICS
  
  // Get interaction data from a trial zip file
  async getTrialInteractionData(studyId, trialId) {
    return getCachedData(`trial_interaction_${studyId}_${trialId}`, async () => {
      try {
        console.log(`Attempting to get interaction data for trial ${trialId} in study ${studyId}...`);
        
        // Try API call with fallback
        const response = await makeApiCallWithFallback(`/analytics/${studyId}/trial-interaction`, {
          params: { trial_id: trialId }
        });
        console.log('Successfully got trial interaction data from API');
        return response.data;
      } catch (error) {
        console.error('Failed to fetch trial interaction data:', error);
        return {
          error: 'Failed to fetch trial interaction data',
          trialId: trialId,
          message: error.message
        };
      }
    });
  },
  
  // Get task details for a specific participant
  async getParticipantTaskDetails(studyId, participantId) {
    return getCachedData(`participant_tasks_${studyId}_${participantId}`, async () => {
      try {
        console.log(`Attempting to get task details for participant ${participantId} in study ${studyId}...`);
        
        // Try API call with fallback
        const response = await makeApiCallWithFallback(`/analytics/${studyId}/participant-task-details`, {
          params: { participant_id: participantId }
        });
        console.log('Successfully got participant task details from API');
        return response.data;
      } catch (error) {
        console.error('Failed to fetch participant task details:', error);
        return [];
      }
    });
  },
  
  // Get aggregated metrics from zip files for a study or participant
  async getZipDataMetrics(studyId, participantId = null) {
    const cacheKey = participantId 
      ? `zip_metrics_${studyId}_participant_${participantId}` 
      : `zip_metrics_${studyId}`;
      
    return getCachedData(cacheKey, async () => {
      try {
        console.log(`Attempting to get zip data metrics for study ${studyId}${participantId ? ' and participant ' + participantId : ''}...`);
        
        // Set up params
        const params = {};
        if (participantId) {
          params.participant_id = participantId;
        }
        
        // Request data from API (starts async process)
        const response = await makeApiCallWithFallback(`/analytics/${studyId}/zip-data`, {
          params
        });
        
        // Check if this is an async job (will have status="processing" and job_id)
        if (response.data && response.data.status === 'processing' && response.data.job_id) {
          console.log(`ZIP processing started asynchronously with job ID: ${response.data.job_id}`);
          
          // Now we need to poll for results
          const jobId = response.data.job_id;
          const maxAttempts = 60;  // Max 60 attempts (with initial pollInterval of 1s)
          let attempts = 0;
          let pollInterval = 1000;  // Start with 1 second intervals
          
          // Define the polling function
          const pollForResults = async () => {
            attempts++;
            
            try {
              // Check job status using our dedicated method
              const jobStatus = await this.checkJobStatus(jobId);
              
              console.log(`Poll attempt ${attempts}/${maxAttempts}: Job status ${jobStatus.status}`);
              
              if (jobStatus.status === 'completed') {
                // Job completed successfully
                console.log('ZIP processing job completed successfully');
                return jobStatus.result;
              } else if (jobStatus.status === 'failed') {
                // Job failed
                console.error('ZIP processing job failed:', jobStatus.error);
                throw new Error(jobStatus.error || 'Processing failed');
              } else if (attempts >= maxAttempts) {
                // Too many attempts
                console.error(`Polling timeout after ${maxAttempts} attempts`);
                throw new Error('Timeout waiting for results');
              } else {
                // Job still in progress, wait and try again
                console.log(`Job still in progress (${jobStatus.status}), waiting ${pollInterval/1000}s before next poll`);
                
                // Increasing poll interval with exponential backoff (max 5 seconds)
                pollInterval = Math.min(pollInterval * 1.2, 5000);
                
                // Wait for the interval then try again
                await new Promise(resolve => setTimeout(resolve, pollInterval));
                return pollForResults();
              }
            } catch (error) {
              console.error(`Error during polling (attempt ${attempts}/${maxAttempts}):`, error);
              if (attempts >= maxAttempts) {
                throw error;
              }
              
              // Wait and try again
              await new Promise(resolve => setTimeout(resolve, pollInterval));
              return pollForResults();
            }
          };
          
          // Start polling
          return await pollForResults();
        } else {
          // Not an async job, return the data directly
          console.log('Successfully got zip data metrics from API immediately');
          return response.data;
        }
      } catch (error) {
        // Special handling for timeout errors
        if (error.message && error.message.includes('timeout')) {
          console.warn('Initial request timed out but the job might still be processing');
          return {
            status: 'timeout',
            error: 'Request timed out. The job may still be processing in the background.',
            message: 'The server request timed out. Try checking the job status in a few seconds.',
            studyId: studyId,
            participantId: participantId
          };
        }
        
        // Other errors
        console.error('Failed to fetch zip data metrics:', error);
        return {
          error: 'Failed to fetch zip data metrics',
          studyId: studyId,
          participantId: participantId,
          message: error.message
        };
      }
    });
  },
  
  // Poll for job status with retries and backoff
  async pollJobUntilComplete(jobId, maxAttempts = 60, initialPollInterval = 1000) {
    let attempts = 0;
    let pollInterval = initialPollInterval;
    
    console.log(`Starting polling for job ${jobId} (max ${maxAttempts} attempts)`);
    
    while (attempts < maxAttempts) {
      attempts++;
      try {
        // Check job status
        const jobStatus = await this.checkJobStatus(jobId);
        console.log(`Poll attempt ${attempts}/${maxAttempts}: Job ${jobId} status: ${jobStatus.status}`);
        
        if (jobStatus.status === 'completed') {
          // Job is done
          return jobStatus.result;
        } else if (jobStatus.status === 'failed') {
          // Job failed
          throw new Error(jobStatus.error || 'Job failed');
        } else if (jobStatus.status === 'not_found') {
          // Job not found
          throw new Error('Job not found');
        }
        
        // If we're here, job is still in progress (queued or running)
        // Wait before checking again
        await new Promise(resolve => setTimeout(resolve, pollInterval));
        
        // Increase poll interval with exponential backoff (max 5 seconds)
        pollInterval = Math.min(pollInterval * 1.2, 5000);
      } catch (error) {
        console.error(`Error polling job ${jobId} (attempt ${attempts}/${maxAttempts}):`, error);
        
        // For most errors, we should retry after waiting
        if (attempts >= maxAttempts) {
          throw new Error(`Polling timed out after ${maxAttempts} attempts: ${error.message}`);
        }
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, pollInterval));
        pollInterval = Math.min(pollInterval * 1.5, 5000); // Increase more aggressively on error
      }
    }
    
    // If we get here, we've run out of attempts
    throw new Error(`Polling timed out after ${maxAttempts} attempts`);
  },
  
  // Check status of an async job
  async checkJobStatus(jobId) {
    try {
      console.log(`Checking status for job ${jobId}...`);
      
      // Try API call with fallback
      const response = await makeApiCallWithFallback(`/analytics/jobs/${jobId}`);
      console.log(`Job ${jobId} status: ${response.data.status}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to check job status for ${jobId}:`, error);
      return {
        job_id: jobId,
        status: 'error',
        error: error.message
      };
    }
  },
  
  // Check queue status
  async getQueueStatus() {
    try {
      console.log('Checking queue status...');
      
      // Try API call with fallback
      const response = await makeApiCallWithFallback('/analytics/queue-status');
      console.log('Queue status:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to check queue status:', error);
      return {
        status: 'error',
        error: error.message
      };
    }
  }
};

export default analyticsApi;