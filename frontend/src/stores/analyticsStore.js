import analyticsApi from '@/api/analyticsApi';

export default {
  namespaced: true,
  
  state: {
    studies: [],
    summaryMetrics: [],
    learningCurveData: [],
    taskPerformanceData: [],
    participantData: []
  },
  
  mutations: {
    SET_STUDIES(state, studies) {
      state.studies = studies;
    },
    
    SET_SUMMARY_METRICS(state, metrics) {
      state.summaryMetrics = metrics;
    },
    
    SET_LEARNING_CURVE_DATA(state, data) {
      state.learningCurveData = data;
    },
    
    SET_TASK_PERFORMANCE_DATA(state, data) {
      state.taskPerformanceData = data;
    },
    
    SET_PARTICIPANT_DATA(state, data) {
      state.participantData = data;
    }
  },
  
  actions: {
    async fetchStudies({ commit }) {
      try {
        const studies = await analyticsApi.getStudies();
        commit('SET_STUDIES', studies);
        return studies;
      } catch (error) {
        console.error('Error fetching studies:', error);
        throw error;
      }
    },
    
    async fetchStudyData({ commit }, studyId) {
      try {
        // Fetch summary metrics
        const summaryMetrics = await analyticsApi.getSummaryMetrics(studyId);
        commit('SET_SUMMARY_METRICS', summaryMetrics);
        
        // Fetch learning curve data
        const learningCurveData = await analyticsApi.getLearningCurveData(studyId);
        commit('SET_LEARNING_CURVE_DATA', learningCurveData);
        
        // Fetch task performance data
        const taskPerformanceData = await analyticsApi.getTaskPerformanceData(studyId);
        commit('SET_TASK_PERFORMANCE_DATA', taskPerformanceData);
        
        // Fetch participant data
        const participantData = await analyticsApi.getParticipantData(studyId);
        commit('SET_PARTICIPANT_DATA', participantData);
        
        return true;
      } catch (error) {
        console.error('Error fetching study data:', error);
        throw error;
      }
    }
  }
};