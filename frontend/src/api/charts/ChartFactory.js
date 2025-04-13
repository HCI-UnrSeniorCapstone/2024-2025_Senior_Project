import LineChart from './LineChart';
import BarChart from './BarChart';
import BubbleChart from './BubbleChart';

/**
 * Factory class for creating different chart types
 */
export default class ChartFactory {
  /**
   * Create a chart based on the specified type
   * @param {string} type - The type of chart to create (line, bar, bubble)
   * @param {HTMLElement} container - DOM element to render the chart in
   * @param {Array} data - Data for the chart
   * @param {Object} options - Configuration options for the chart
   * @returns {ChartBase} The created chart instance
   */
  static createChart(type, container, data, options = {}) {
    switch (type.toLowerCase()) {
      case 'line':
        return new LineChart(container, data, options);
      
      case 'bar':
        return new BarChart(container, data, options);
      
      case 'bubble':
        return new BubbleChart(container, data, options);
      
      default:
        throw new Error(`Unsupported chart type: ${type}`);
    }
  }
}
