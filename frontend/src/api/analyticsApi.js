import axios from 'axios';

const API_BASE_URL = process.env.VUE_APP_API_URL || '/api';

const analyticsApi = {
  /**
   * Get list of all available studies
   */
  async getStudies() {
    const response = await axios.get(`${API_BASE_URL}/studies`);
    return response.data;
  },

  /**
   * Get summary metrics for a study
   * @param {string} studyId - ID of the study
   */
  async getSummaryMetrics(studyId) {
    const response = await axios.get(`${API_BASE_URL}/analytics/${studyId}/summary`);
    return response.data;
  },

  /**
   * Get learning curve data for a study
   * @param {string} studyId - ID of the study
   */
  async getLearningCurveData(studyId) {
    const response = await axios.get(`${API_BASE_URL}/analytics/${studyId}/learning-curve`);
    return response.data;
  },

  /**
   * Get task performance comparison data
   * @param {string} studyId - ID of the study
   */
  async getTaskPerformanceData(studyId) {
    const response = await axios.get(`${API_BASE_URL}/analytics/${studyId}/task-performance`);
    return response.data;
  },

  /**
   * Get participant data for a study
   * @param {string} studyId - ID of the study
   */
  async getParticipantData(studyId) {
    const response = await axios.get(`${API_BASE_URL}/analytics/${studyId}/participants`);
    return response.data;
  },

  /**
   * Export study data in specified format
   * @param {string} studyId - ID of the study
   * @param {string} format - Export format (csv, json)
   */
  async exportStudyData(studyId, format = 'csv') {
    const response = await axios.get(
      `${API_BASE_URL}/analytics/${studyId}/export`,
      {
        params: { format },
        responseType: 'blob'
      }
    );
    return response.data;
  }
};

export default analyticsApi;