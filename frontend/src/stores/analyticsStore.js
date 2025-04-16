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
    
    // Loading states
    loading: {
      studies: false,
      summaryMetrics: false,
      learningCurve: false,
      taskPerformance: false,
      participants: false,
      all: false
    },
    
    // Error states
    errors: {
      studies: null,
      summaryMetrics: null,
      learningCurve: null,
      taskPerformance: null,
      participants: null,
      all: null
    },

    // Last updated timestamps
    lastUpdated: {
      studies: null,
      summaryMetrics: null,
      learningCurve: null,
      taskPerformance: null,
      participants: null
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
    
    // Loading state getters
    isLoading: (state) => Object.values(state.loading).some(Boolean),
    isLoadingStudies: (state) => state.loading.studies,
    isLoadingSummaryMetrics: (state) => state.loading.summaryMetrics,
    isLoadingLearningCurve: (state) => state.loading.learningCurve,
    isLoadingTaskPerformance: (state) => state.loading.taskPerformance,
    isLoadingParticipants: (state) => state.loading.participants,
    
    // Error state getters
    hasErrors: (state) => Object.values(state.errors).some(Boolean),
    getStudiesError: (state) => state.errors.studies,
    getSummaryMetricsError: (state) => state.errors.summaryMetrics,
    getLearningCurveError: (state) => state.errors.learningCurve,
    getTaskPerformanceError: (state) => state.errors.taskPerformance,
    getParticipantsError: (state) => state.errors.participants,
    
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