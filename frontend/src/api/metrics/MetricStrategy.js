// Abstract base class for metrics calculations
export default class MetricStrategy {
  constructor() {
    if (this.constructor === MetricStrategy) {
      throw new Error('MetricStrategy is an abstract class and cannot be instantiated directly');
    }
  }
  
  // Calculate metric value from data (implement in subclasses)
  calculate(data) {
    throw new Error('Method calculate() must be implemented by subclass');
  }
  
  // Get info about this metric
  getMetadata() {
    return {
      name: 'Abstract Metric',
      description: 'Base metric strategy',
      unit: ''
    };
  }
}
