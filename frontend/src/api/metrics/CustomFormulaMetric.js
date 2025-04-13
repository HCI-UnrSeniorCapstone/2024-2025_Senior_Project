import MetricStrategy from './MetricStrategy';

/**
 * Strategy for calculating metrics using custom formulas
 */
export default class CustomFormulaMetric extends MetricStrategy {
  /**
   * Create a custom formula metric
   * @param {Object} options - Configuration options
   * @param {Function} options.formula - The formula function to calculate the metric
   * @param {string} options.name - Name of the metric
   * @param {string} options.description - Description of the metric
   * @param {string} options.unit - Unit of measurement
   */
  constructor(options) {
    super();
    
    if (typeof options.formula !== 'function') {
      throw new Error('CustomFormulaMetric requires a formula function');
    }
    
    this.formula = options.formula;
    this.metadata = {
      name: options.name || 'Custom Metric',
      description: options.description || 'Custom metric with user-defined formula',
      unit: options.unit || ''
    };
  }
  
  /**
   * Calculate the metric using the custom formula
   * @param {any} data - Data to pass to the custom formula
   * @returns {any} Result of the custom formula
   */
  calculate(data) {
    return this.formula(data);
  }
  
  /**
   * Get metadata about this metric
   * @returns {Object} Metadata including name, description, and unit
   */
  getMetadata() {
    return this.metadata;
  }
}
