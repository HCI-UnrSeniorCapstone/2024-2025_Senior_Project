/**
 * Base class for chart implementations
 */
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
  
  /**
   * Initialize the chart (to be implemented by subclasses)
   */
  initialize() {
    throw new Error('Method initialize() must be implemented by subclass');
  }
  
  /**
   * Render the chart (to be implemented by subclasses)
   */
  render() {
    throw new Error('Method render() must be implemented by subclass');
  }
  
  /**
   * Update the chart with new data
   * @param {Array} newData - New data for the chart
   */
  updateData(newData) {
    this.data = newData;
    this.render();
  }
  
  /**
   * Update chart options
   * @param {Object} newOptions - New options to apply to the chart
   */
  updateOptions(newOptions) {
    this.options = {
      ...this.options,
      ...newOptions
    };
    this.render();
  }
  
  /**
   * Cleanup method to be called when chart is no longer needed
   */
  destroy() {
    // Default implementation - can be overridden by subclasses
    // to provide proper cleanup logic
  }
}
