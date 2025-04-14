// Base class for all chart types
export default class ChartBase {
  constructor(container, data, options = {}) {
    if (this.constructor === ChartBase) {
      throw new Error('ChartBase is an abstract class and cannot be instantiated directly');
    }
    
    this.container = container;
    this.data = data;
    this.options = {
      width: 800,
      height: 400,
      margin: { top: 20, right: 30, bottom: 40, left: 50 },
      ...options
    };
    
    this.initialize();
  }
  
  // Must be implemented by child classes
  initialize() {
    throw new Error('Method initialize() must be implemented by subclass');
  }
  
  // Must be implemented by child classes
  render() {
    throw new Error('Method render() must be implemented by subclass');
  }
  
  // Updates chart data and rerenders
  updateData(newData) {
    this.data = newData;
    this.render();
  }
  
  // Updates chart config options and rerenders
  updateOptions(newOptions) {
    this.options = {
      ...this.options,
      ...newOptions
    };
    this.render();
  }
  
  // Cleanup resources - override in subclasses as needed
  destroy() {
    // Default empty implementation
  }
}
