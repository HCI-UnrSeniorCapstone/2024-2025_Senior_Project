import TimePerTaskMetric from './TimePerTaskMetric';
import CompletionRateMetric from './CompletionRateMetric';
import PValueMetric from './PValueMetric';

// Registry that manages all available metrics (singleton)
export default class MetricRegistry {
  constructor() {
    if (MetricRegistry.instance) {
      return MetricRegistry.instance;
    }
    
    this.metrics = new Map();
    this.registerDefaultMetrics();
    
    MetricRegistry.instance = this;
  }
  
  // Sets up the built-in metrics
  registerDefaultMetrics() {
    // Register time metrics with different aggregations
    this.register('meanTimePerTask', new TimePerTaskMetric({ aggregation: 'mean' }));
    this.register('medianTimePerTask', new TimePerTaskMetric({ aggregation: 'median' }));
    this.register('minTimePerTask', new TimePerTaskMetric({ aggregation: 'min' }));
    this.register('maxTimePerTask', new TimePerTaskMetric({ aggregation: 'max' }));
    
    // Register other default metrics
    this.register('completionRate', new CompletionRateMetric());
    this.register('pValue', new PValueMetric());
  }
  
  // Add a new metric to the registry
  register(key, metric) {
    this.metrics.set(key, metric);
  }
  
  // Look up a metric by its key
  getMetric(key) {
    return this.metrics.has(key) ? this.metrics.get(key) : null;
  }
  
  // Run calculation for the specified metric
  calculate(key, data) {
    const metric = this.getMetric(key);
    return metric ? metric.calculate(data) : null;
  }
  
  // Get list of all registered metrics
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
