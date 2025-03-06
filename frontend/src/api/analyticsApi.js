import axios from 'axios';

const API_BASE_URL = process.env.VUE_APP_API_URL || '/api';

const analyticsApi = {
  
  // Fetch all the studies 
  async getStudies() {
    const response = await axios.get(`${API_BASE_URL}/analytics/studies`);
    return response.data;
  },

  // Get summary data for a specific study
  // studyId is the unique identifier for the study
  async getSummaryMetrics(studyId) {
    const response = await axios.get(`${API_BASE_URL}/analytics/${studyId}/summary`);
    return response.data;
  },

  
  // Get learning curve info for a study
  // studyId is the ID of the study you're interested in
  async getLearningCurveData(studyId) {
    const response = await axios.get(`${API_BASE_URL}/analytics/${studyId}/learning-curve`);
    return response.data;
  },

  
  // Get task performance data for a study
  // studyId again is needed here
  async getTaskPerformanceData(studyId) {
    const response = await axios.get(`${API_BASE_URL}/analytics/${studyId}/task-performance`);
    return response.data;
  },

  
  // Get participant data for a specific study
  // This includes all participants involved in the study
  async getParticipantData(studyId) {
    const response = await axios.get(`${API_BASE_URL}/analytics/${studyId}/participants`);
    return response.data;
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