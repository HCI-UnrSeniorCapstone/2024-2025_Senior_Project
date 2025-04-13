import TimePerTaskMetric from './TimePerTaskMetric';
import CompletionRateMetric from './CompletionRateMetric';
import ErrorRateMetric from './ErrorRateMetric';

/**
 * Registry of available metrics
 * Singleton pattern to provide global access to metric instances
 */
export default class MetricRegistry {
  constructor() {
    if (MetricRegistry.instance) {
      return MetricRegistry.instance;
    }
    
    this.metrics = new Map();
    this.registerDefaultMetrics();
    
    MetricRegistry.instance = this;
  }
  
  /**
   * Register built-in default metrics
   */
  registerDefaultMetrics() {
    // Register time-based metrics with different aggregations
    this.register('meanTimePerTask', new TimePerTaskMetric({ aggregation: 'mean' }));
    this.register('medianTimePerTask', new TimePerTaskMetric({ aggregation: 'median' }));
    this.register('minTimePerTask', new TimePerTaskMetric({ aggregation: 'min' }));
    this.register('maxTimePerTask', new TimePerTaskMetric({ aggregation: 'max' }));
    
    // Register other default metrics
    this.register('completionRate', new CompletionRateMetric());
    this.register('errorRate', new ErrorRateMetric());
  }
  
  /**
   * Register a new metric
   * @param {string} key - The key to identify the metric
   * @param {MetricStrategy} metric - The metric strategy instance
   */
  register(key, metric) {
    this.metrics.set(key, metric);
  }
  
  /**
   * Get a metric by key
   * @param {string} key - The key of the metric to retrieve
   * @returns {MetricStrategy|null} The metric strategy, or null if not found
   */
  getMetric(key) {
    return this.metrics.has(key) ? this.metrics.get(key) : null;
  }
  
  /**
   * Calculate a metric from data
   * @param {string} key - The key of the metric to calculate
   * @param {any} data - The data to calculate the metric from
   * @returns {any} The calculated metric value, or null if metric not found
   */
  calculate(key, data) {
    const metric = this.getMetric(key);
    return metric ? metric.calculate(data) : null;
  }
  
  /**
   * Get a list of all available metrics
   * @returns {Array} Array of objects with key and metadata for each metric
   */
  getAvailableMetrics() {
    const result = [];
    this.metrics.forEach((metric, key) => {
      result.push({
        key,
        ...metric.getMetadata()
      });
    });
    return result;
  }
}
