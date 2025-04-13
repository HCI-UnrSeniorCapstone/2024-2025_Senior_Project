import Repository from './Repository';
import analyticsApi from '../analyticsApi';

/**
 * Repository for analytics data
 */
export default class AnalyticsRepository extends Repository {
  constructor() {
    super();
    this.apiClient = analyticsApi;
  }
  
  /**
   * Get all available studies
   * @returns {Promise<Array>} Promise resolving to array of studies
   */
  async findAllStudies() {
    try {
      return await this.apiClient.getStudies();
    } catch (error) {
      console.error('Error fetching studies:', error);
      return [];
    }
  }
  
  /**
   * Get summary data for a study
   * @param {string|number} studyId - The ID of the study
   * @returns {Promise<Object>} Promise resolving to study summary data
   */
  async getStudySummary(studyId) {
    try {
      return await this.apiClient.getSummaryMetrics(studyId);
    } catch (error) {
      console.error(`Error fetching summary for study ${studyId}:`, error);
      return {};
    }
  }
  
  /**
   * Get learning curve data for a study
   * @param {string|number} studyId - The ID of the study
   * @returns {Promise<Array>} Promise resolving to learning curve data
   */
  async getLearningCurveData(studyId) {
    try {
      return await this.apiClient.getLearningCurveData(studyId);
    } catch (error) {
      console.error(`Error fetching learning curve data for study ${studyId}:`, error);
      return [];
    }
  }
  
  /**
   * Get task performance comparison data for a study
   * @param {string|number} studyId - The ID of the study
   * @returns {Promise<Array>} Promise resolving to task performance data
   */
  async getTaskPerformanceData(studyId) {
    try {
      return await this.apiClient.getTaskPerformanceData(studyId);
    } catch (error) {
      console.error(`Error fetching task performance data for study ${studyId}:`, error);
      return [];
    }
  }
  
  /**
   * Get participant data for a study
   * @param {string|number} studyId - The ID of the study
   * @returns {Promise<Array>} Promise resolving to participant data
   */
  async getParticipantData(studyId) {
    try {
      return await this.apiClient.getParticipantData(studyId);
    } catch (error) {
      console.error(`Error fetching participant data for study ${studyId}:`, error);
      return [];
    }
  }
  
  /**
   * Export study data in specified format
   * @param {string|number} studyId - The ID of the study
   * @param {string} format - The export format (e.g., 'csv', 'json')
   * @returns {Promise<Blob>} Promise resolving to the exported data blob
   */
  async exportStudyData(studyId, format = 'csv') {
    try {
      return await this.apiClient.exportStudyData(studyId, format);
    } catch (error) {
      console.error(`Error exporting data for study ${studyId}:`, error);
      throw error;
    }
  }
  
  /**
   * These methods are inherited from Repository but not applicable
   * for analytics (read-only data)
   */
  async findAll() {
    return this.findAllStudies();
  }
  
  async findById(id) {
    return this.getStudySummary(id);
  }
  
  async save() {
    throw new Error('Analytics data is read-only and cannot be saved');
  }
  
  async delete() {
    throw new Error('Analytics data is read-only and cannot be deleted');
  }
}
