import MetricStrategy from './MetricStrategy';

/**
 * Strategy for calculating error rate metrics
 */
export default class ErrorRateMetric extends MetricStrategy {
  /**
   * Calculate error rate from task result data
   * @param {Array} taskResults - Array of task results with errors count
   * @returns {Object} Metrics by task and overall
   */
  calculate(taskResults) {
    if (!Array.isArray(taskResults) || taskResults.length === 0) {
      return { overall: 0, byTask: {} };
    }
    
    // Group by task
    const taskGroups = {};
    taskResults.forEach(result => {
      const taskId = result.taskId || result.task_id;
      if (!taskGroups[taskId]) {
        taskGroups[taskId] = {
          attempts: 0,
          errors: 0
        };
      }
      
      taskGroups[taskId].attempts++;
      if (result.errors) {
        taskGroups[taskId].errors += result.errors;
      }
    });
    
    // Calculate error rate for each task (errors per attempt)
    const byTask = {};
    let totalErrors = 0;
    let totalAttempts = 0;
    
    Object.entries(taskGroups).forEach(([taskId, counts]) => {
      byTask[taskId] = counts.attempts > 0 ? counts.errors / counts.attempts : 0;
      totalErrors += counts.errors;
      totalAttempts += counts.attempts;
    });
    
    // Calculate overall error rate
    const overall = totalAttempts > 0 ? totalErrors / totalAttempts : 0;
    
    return { overall, byTask };
  }
  
  /**
   * Get metadata about this metric
   * @returns {Object} Metadata including name, description, and unit
   */
  getMetadata() {
    return {
      name: 'Error Rate',
      description: 'Average number of errors per task attempt',
      unit: 'errors/attempt'
    };
  }
}
