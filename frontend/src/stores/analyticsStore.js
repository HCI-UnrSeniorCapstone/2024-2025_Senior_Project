import { defineStore } from 'pinia';
import analyticsApi from '@/api/analyticsApi';
import MetricRegistry from '@/api/metrics/MetricRegistry';
import CustomFormulaMetric from '@/api/metrics/CustomFormulaMetric';

// Analytics store for managing data related to analytics features
export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    // Data states
    studies: [],
    summaryMetrics: {},
    learningCurveData: [],
    taskPerformanceData: [],
    participantData: [],
    customMetrics: {},
    
    // New data states for zip analytics
    trialInteractionData: {}, // { trialId: data }
    zipDataMetrics: {}, // { studyId: data } or { studyId_participantId: data }
    
    // Loading states
    loading: {
      studies: false,
      summaryMetrics: false,
      learningCurve: false,
      taskPerformance: false,
      participants: false,
      trialInteraction: false,
      zipDataMetrics: false,
      all: false
    },
    
    // Error states
    errors: {
      studies: null,
      summaryMetrics: null,
      learningCurve: null,
      taskPerformance: null,
      participants: null,
      trialInteraction: null,
      zipDataMetrics: null,
      all: null
    },

    // Last updated timestamps
    lastUpdated: {
      studies: null,
      summaryMetrics: null,
      learningCurve: null,
      taskPerformance: null,
      participants: null,
      trialInteraction: null,
      zipDataMetrics: null
    },
    
    // Metric registry instance
    metricRegistry: new MetricRegistry()
  }),
  
  getters: {
    // Data getters
    getStudies: (state) => state.studies,
    getSummaryMetrics: (state) => state.summaryMetrics,
    getLearningCurveData: (state) => state.learningCurveData,
    getTaskPerformanceData: (state) => state.taskPerformanceData,
    getParticipantData: (state) => state.participantData,
    getCustomMetrics: (state) => state.customMetrics,
    getAvailableMetrics: (state) => state.metricRegistry.getAvailableMetrics(),
    
    // Zip data getters
    getTrialInteractionData: (state) => (trialId) => state.trialInteractionData[trialId],
    getZipDataMetrics: (state) => (studyId, participantId = null) => {
      const key = participantId ? `${studyId}_${participantId}` : `${studyId}`;
      return state.zipDataMetrics[key];
    },
    
    // Loading state getters
    isLoading: (state) => Object.values(state.loading).some(Boolean),
    isLoadingStudies: (state) => state.loading.studies,
    isLoadingSummaryMetrics: (state) => state.loading.summaryMetrics,
    isLoadingLearningCurve: (state) => state.loading.learningCurve,
    isLoadingTaskPerformance: (state) => state.loading.taskPerformance,
    isLoadingParticipants: (state) => state.loading.participants,
    isLoadingTrialInteraction: (state) => state.loading.trialInteraction,
    isLoadingZipDataMetrics: (state) => state.loading.zipDataMetrics,
    
    // Error state getters
    hasErrors: (state) => Object.values(state.errors).some(Boolean),
    getStudiesError: (state) => state.errors.studies,
    getSummaryMetricsError: (state) => state.errors.summaryMetrics,
    getLearningCurveError: (state) => state.errors.learningCurve,
    getTaskPerformanceError: (state) => state.errors.taskPerformance,
    getParticipantsError: (state) => state.errors.participants,
    getTrialInteractionError: (state) => state.errors.trialInteraction,
    getZipDataMetricsError: (state) => state.errors.zipDataMetrics,
    
    // Get data freshness
    getLastUpdated: (state) => state.lastUpdated
  },
  
  actions: {
    // Fetch all available studies
    async fetchStudies() {
      this.loading.studies = true;
      this.errors.studies = null;
      
      try {
        console.log('Store: Fetching studies...');
        const studies = await analyticsApi.getStudies();
        
        // Reset studies array to ensure no duplicates
        this.studies = [];
        
        // Add the new studies
        this.studies = studies;
        console.log('Store: Studies updated with ', studies.length, 'items');
        
        this.lastUpdated.studies = new Date().toISOString();
        return studies;
      } catch (error) {
        console.error('Store: Error fetching studies:', error);
        this.errors.studies = error.message || 'Error fetching studies';
        throw error;
      } finally {
        this.loading.studies = false;
      }
    },
    
    // Fetch summary metrics for a study
    async fetchSummaryMetrics(studyId) {
      this.loading.summaryMetrics = true;
      this.errors.summaryMetrics = null;
      
      try {
        const metrics = await analyticsApi.getSummaryMetrics(studyId);
        this.summaryMetrics = metrics;
        this.lastUpdated.summaryMetrics = new Date().toISOString();
        return metrics;
      } catch (error) {
        this.errors.summaryMetrics = error.message || `Error fetching summary metrics for study ${studyId}`;
        throw error;
      } finally {
        this.loading.summaryMetrics = false;
      }
    },
    
    // Fetch learning curve data for a study
    async fetchLearningCurve(studyId) {
      this.loading.learningCurve = true;
      this.errors.learningCurve = null;
      
      try {
        const data = await analyticsApi.getLearningCurveData(studyId);
        this.learningCurveData = data;
        this.lastUpdated.learningCurve = new Date().toISOString();
        return data;
      } catch (error) {
        this.errors.learningCurve = error.message || `Error fetching learning curve data for study ${studyId}`;
        throw error;
      } finally {
        this.loading.learningCurve = false;
      }
    },
    
    // Fetch task performance data for a study
    async fetchTaskPerformance(studyId) {
      this.loading.taskPerformance = true;
      this.errors.taskPerformance = null;
      
      try {
        const data = await analyticsApi.getTaskPerformanceData(studyId);
        this.taskPerformanceData = data;
        this.lastUpdated.taskPerformance = new Date().toISOString();
        return data;
      } catch (error) {
        this.errors.taskPerformance = error.message || `Error fetching task performance data for study ${studyId}`;
        throw error;
      } finally {
        this.loading.taskPerformance = false;
      }
    },
    
    // Fetch participant data for a study (with pagination)
    async fetchParticipants(studyId, page = 1, pageSize = 20) {
      this.loading.participants = true;
      this.errors.participants = null;
      
      try {
        const data = await analyticsApi.getParticipantData(studyId, page, pageSize);
        this.participantData = data;
        this.lastUpdated.participants = new Date().toISOString();
        return data;
      } catch (error) {
        this.errors.participants = error.message || `Error fetching participant data for study ${studyId}`;
        throw error;
      } finally {
        this.loading.participants = false;
      }
    },
    
    // Fetch trial interaction data from zip
    async fetchTrialInteractionData(studyId, trialId) {
      this.loading.trialInteraction = true;
      this.errors.trialInteraction = null;
      
      try {
        console.log(`Store: Fetching trial interaction data for trial ${trialId}...`);
        const data = await analyticsApi.getTrialInteractionData(studyId, trialId);
        
        // Store in state
        this.trialInteractionData = {
          ...this.trialInteractionData,
          [trialId]: data
        };
        
        this.lastUpdated.trialInteraction = new Date().toISOString();
        return data;
      } catch (error) {
        console.error(`Store: Error fetching trial interaction data for trial ${trialId}:`, error);
        this.errors.trialInteraction = error.message || `Error fetching trial interaction data`;
        throw error;
      } finally {
        this.loading.trialInteraction = false;
      }
    },
    
    // Fetch zip data metrics for a study or participant
    async fetchZipDataMetrics(studyId, participantId = null) {
      this.loading.zipDataMetrics = true;
      this.errors.zipDataMetrics = null;
      
      try {
        console.log(`Store: Fetching zip data metrics for study ${studyId}${participantId ? ' and participant ' + participantId : ''}...`);
        
        // Generate a key for storage
        const key = participantId ? `${studyId}_${participantId}` : `${studyId}`;
        
        // First check if we already have this data cached
        if (this.zipDataMetrics[key] && !this.zipDataMetrics[key].error) {
          console.log(`Store: Using cached zip data for study ${studyId}`);
          this.loading.zipDataMetrics = false;
          return this.zipDataMetrics[key];
        }
        
        // If not in cache or cached with error, try to fetch
        try {
          const data = await analyticsApi.getZipDataMetrics(studyId, participantId);
          
          // Check if we got valid data
          if (!data) {
            console.error('Store: Received null or undefined data from API');
            throw new Error('No data received from API');
          }
          
          // Special handling for async job responses
          if (data.status === 'processing' && data.job_id) {
            console.log(`Store: Got async job ID ${data.job_id}, will return this for polling`);
            
            // We'll store this as-is, but it's not the final result
            this.zipDataMetrics = {
              ...this.zipDataMetrics,
              [key]: data
            };
            
            return data;
          }
          
          // Handle returned errors
          if (data.error) {
            console.error(`Store: API returned error: ${data.error}`);
            throw new Error(data.error);
          }
          
          console.log(`Store: Zip data fetch successful for study ${studyId}, keys:`, Object.keys(data));
          
          // Store in state
          this.zipDataMetrics = {
            ...this.zipDataMetrics,
            [key]: data
          };
          
          this.lastUpdated.zipDataMetrics = new Date().toISOString();
          return data;
        } catch (apiError) {
          // Handle the case where the initial API call fails with timeout
          if (apiError.message && apiError.message.includes('timeout')) {
            console.warn('Store: API request timed out, returning a timeout status for polling');
            
            // Create a response that looks like an async job response but indicates timeout
            const timeoutResponse = {
              status: 'timeout',
              error: 'Request timed out. The worker might still be processing the data.',
              message: 'The server request timed out, but the job might still be running in the background.',
              studyId: studyId,
              participantId: participantId,
              retry_in: 5000 // Suggest a retry in 5 seconds
            };
            
            // Cache this timeout response
            this.zipDataMetrics = {
              ...this.zipDataMetrics,
              [key]: timeoutResponse
            };
            
            // We'll still count this as an error for the UI
            this.errors.zipDataMetrics = 'Request timed out. Try checking the job status again in a few seconds.';
            
            return timeoutResponse;
          }
          
          // For other errors, pass through
          throw apiError;
        }
      } catch (error) {
        console.error(`Store: Error fetching zip data metrics:`, error);
        this.errors.zipDataMetrics = error.message || `Error fetching zip data metrics`;
        
        // Return the error as structured data so components can handle it
        const errorData = {
          error: error.message || 'Unknown error',
          studyId: studyId,
          participantId: participantId
        };
        
        // Also cache the error so we don't keep retrying the same failing request
        const key = participantId ? `${studyId}_${participantId}` : `${studyId}`;
        this.zipDataMetrics = {
          ...this.zipDataMetrics,
          [key]: errorData
        };
        
        return errorData;
      } finally {
        this.loading.zipDataMetrics = false;
      }
    },
    
    // Fetch all data for a study in parallel
    async fetchAllStudyData(studyId) {
      this.loading.all = true;
      this.errors.all = null;
      
      try {
        await Promise.all([
          this.fetchSummaryMetrics(studyId),
          this.fetchLearningCurve(studyId),
          this.fetchTaskPerformance(studyId),
          this.fetchParticipants(studyId)
        ]);
        
        return true;
      } catch (error) {
        this.errors.all = error.message || 'Error fetching complete study data';
        throw error;
      } finally {
        this.loading.all = false;
      }
    },
    
    // Register a custom metric
    registerCustomMetric(key, metric) {
      this.metricRegistry.register(key, metric);
      this.customMetrics[key] = {
        name: metric.getMetadata().name,
        description: metric.getMetadata().description,
        timestamp: new Date().toISOString()
      };
    },
    
    // Calculate a custom metric with current data
    calculateCustomMetric(metricKey, studyId) {
      // Get the requested metric from registry
      const metric = this.metricRegistry.getMetric(metricKey);
      if (!metric) {
        console.error(`Metric ${metricKey} not found`);
        return null;
      }
      
      // Get combined data for calculation
      let dataForCalculation = [];
      
      // Add task performance data
      if (this.taskPerformanceData && this.taskPerformanceData.length) {
        dataForCalculation = [...dataForCalculation, ...this.taskPerformanceData];
      }
      
      // Add participant data if available
      if (this.participantData && this.participantData.items) {
        dataForCalculation = [...dataForCalculation, ...this.participantData.items];
      }
      
      // Calculate the metric
      const result = metric.calculate(dataForCalculation);
      
      // Store the result
      this.customMetrics[metricKey] = {
        ...this.customMetrics[metricKey],
        result,
        lastCalculated: new Date().toISOString()
      };
      
      return result;
    },
    
    // Reset all store data
    resetStore() {
      this.studies = [];
      this.summaryMetrics = {};
      this.learningCurveData = [];
      this.taskPerformanceData = [];
      this.participantData = [];
      this.customMetrics = {};
      this.trialInteractionData = {};
      this.zipDataMetrics = {};
      
      // Reset all loading states
      Object.keys(this.loading).forEach(key => {
        this.loading[key] = false;
      });
      
      // Reset all error states
      Object.keys(this.errors).forEach(key => {
        this.errors[key] = null;
      });
      
      // Reset all timestamps
      Object.keys(this.lastUpdated).forEach(key => {
        this.lastUpdated[key] = null;
      });
      
      // Reinitialize metric registry
      this.metricRegistry = new MetricRegistry();
    }
  }
});