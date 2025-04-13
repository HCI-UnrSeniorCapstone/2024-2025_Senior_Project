/**
 * Abstract base class for metric calculation strategies
 * Following the Strategy pattern for flexible calculation methods
 */
export default class MetricStrategy {
  constructor() {
    if (this.constructor === MetricStrategy) {
      throw new Error('MetricStrategy is an abstract class and cannot be instantiated directly');
    }
  }
  
  /**
   * Calculate the metric value from the provided data
   * @param {Array|Object} data - The data to calculate the metric from
   * @returns {number|Object} The calculated metric value
   */
  calculate(data) {
    throw new Error('Method calculate() must be implemented by subclass');
  }
  
  /**
   * Get metadata about this metric
   * @returns {Object} Metadata including name, description, and unit
   */
  getMetadata() {
    return {
      name: 'Abstract Metric',
      description: 'Base metric strategy',
      unit: ''
    };
  }
}
