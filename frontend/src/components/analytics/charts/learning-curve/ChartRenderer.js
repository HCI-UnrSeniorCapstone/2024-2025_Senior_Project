import * as d3 from 'd3'
import TimeRenderer from './renderers/TimeRenderer'
import MouseRenderer from './renderers/MouseRenderer'
import KeyboardRenderer from './renderers/KeyboardRenderer'

/**
 * ChartRenderer handles the D3 rendering for the Learning Curve Chart
 */
class ChartRenderer {
  /**
   * Constructor for the chart renderer
   * @param {Object} config - Configuration options for the chart
   */
  constructor(config = {}) {
    this.chart = null
    this.width = 0
    this.height = 0
    this.margin = config.margin || { top: 40, right: 80, bottom: 80, left: 60 }

    // Initialize the metric-specific renderers
    this.renderers = {
      time: new TimeRenderer(),
      mouse: new MouseRenderer(),
      keyboard: new KeyboardRenderer(),
    }
  }

  /**
   * Check if the chart has been initialized
   * @returns {Boolean} - True if chart is initialized
   */
  isInitialized() {
    return this.chart !== null
  }

  /**
   * Initialize the chart with the container element
   * @param {HTMLElement} container - The DOM element to contain the chart
   */
  initChart(container) {
    if (!container) return

    // Start fresh by removing any existing chart
    d3.select(container).selectAll('*').remove()

    // Set dimensions based on container size
    this.width = container.clientWidth - this.margin.left - this.margin.right
    this.height = 400 - this.margin.top - this.margin.bottom

    // Create SVG with responsive viewBox
    const svg = d3
      .select(container)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr(
        'viewBox',
        `0 0 ${this.width + this.margin.left + this.margin.right} ${this.height + this.margin.top + this.margin.bottom + 20}`,
      )
      .attr('preserveAspectRatio', 'xMidYMid meet')

    this.chart = svg
      .append('g')
      .attr('transform', `translate(${this.margin.left},${this.margin.top})`)

    // Create axis placeholders
    this.chart
      .append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${this.height})`)

    this.chart.append('g').attr('class', 'y-axis')

    // Add axis labels
    this.chart
      .append('text')
      .attr('class', 'x-label')
      .attr('text-anchor', 'middle')
      .attr('x', this.width / 2)
      .attr('y', this.height + 70)
      .text('Attempt Number')
      .style('font-size', '12px')
      .style('fill', '#666')

    this.chart
      .append('text')
      .attr('class', 'y-label')
      .attr('text-anchor', 'middle')
      .attr(
        'transform',
        `translate(${-this.margin.left + 15},${this.height / 2}) rotate(-90)`,
      )
      .text('Completion Time (s)')
      .style('font-size', '12px')
      .style('fill', '#666')

    // Placeholder for the legend
    this.chart
      .append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${this.width + 10}, 0)`)
  }

  /**
   * Handle chart resize
   * @param {HTMLElement} container - The DOM element containing the chart
   */
  resize(container) {
    if (!container || !this.chart) return

    // Remove existing chart and reinitialize
    d3.select(container).select('svg').remove()
    this.initChart(container)
  }

  /**
   * Render the "All Tasks" view with averaged data
   * @param {Object} options - Rendering options
   * @param {Array} options.data - The processed data
   * @param {String} options.metric - The selected metric
   */
  renderAllTasksView({ data, metric }) {
    if (!this.chart || data.length === 0) return

    // Update Y-axis label based on metric
    this.updateYAxisLabel(metric)

    // Get the appropriate renderer for the metric
    const renderer = this.renderers[metric] || this.renderers.time

    // Set up scales
    const scales = this.createScales(data, metric)

    // Update axes
    this.updateAxes(scales)

    // Clear existing elements
    this.clearChartElements()

    // Add horizontal grid lines
    this.addGridLines(scales.y)

    // Use the renderer to draw the chart
    renderer.renderAllTasksView({
      chart: this.chart,
      data,
      scales,
      height: this.height,
    })
  }

  /**
   * Render the "Individual Tasks" view with task-specific lines
   * @param {Object} options - Rendering options
   * @param {Array} options.data - The processed data
   * @param {String} options.metric - The selected metric
   */
  renderIndividualTasksView({ data, metric }) {
    if (!this.chart || data.length === 0) return

    // Update Y-axis label based on metric
    this.updateYAxisLabel(metric)

    // Get the appropriate renderer for the metric
    const renderer = this.renderers[metric] || this.renderers.time

    // Prepare scales for multiple tasks
    const scales = this.createScalesForMultipleTasks(data, metric)

    // Update axes
    this.updateAxes(scales)

    // Clear existing elements
    this.clearChartElements()

    // Add horizontal grid lines
    this.addGridLines(scales.y)

    // Use color scale for multiple tasks
    const colorScale = d3.scaleOrdinal(d3.schemeCategory10)

    // Use the renderer to draw the chart
    renderer.renderIndividualTasksView({
      chart: this.chart,
      data,
      scales,
      colorScale,
      height: this.height,
    })

    // Update the legend
    this.updateLegend(data, metric, colorScale)
  }

  /**
   * Update the Y-axis label based on the metric
   * @param {String} metric - The selected metric (time|mouse|keyboard)
   */
  updateYAxisLabel(metric) {
    let yAxisLabel = 'Completion Time (s)'

    if (metric === 'mouse') {
      yAxisLabel = 'Mouse Movement (pixels)'
    } else if (metric === 'keyboard') {
      yAxisLabel = 'Keyboard Actions (count)'
    }

    this.chart.select('.y-label').text(yAxisLabel)
  }

  /**
   * Create scales for the "All Tasks" view
   * @param {Array} data - The processed data
   * @param {String} metric - The selected metric
   * @returns {Object} - x and y scales
   */
  createScales(data, metric) {
    // Determine which value to use for scaling
    const valueKey = this.getValueKeyForMetric(metric)

    // Create scales
    const x = d3
      .scaleLinear()
      .domain([1, d3.max(data, d => d.attempt)])
      .range([0, this.width])

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, d => d[valueKey]) * 1.1])
      .range([this.height, 0])

    return { x, y, valueKey }
  }

  /**
   * Create scales for the "Individual Tasks" view with multiple tasks
   * @param {Array} data - The processed data grouped by task
   * @param {String} metric - The selected metric
   * @returns {Object} - x and y scales
   */
  createScalesForMultipleTasks(data, metric) {
    // Determine which value to use for scaling
    const valueKey = this.getValueKeyForMetric(metric)

    // Find max values across all tasks
    const maxAttempt = d3.max(data, d => d3.max(d.data, item => item.attempt))
    const maxValue = d3.max(data, d => d3.max(d.data, item => item[valueKey]))

    // Create scales
    const x = d3.scaleLinear().domain([1, maxAttempt]).range([0, this.width])

    const y = d3
      .scaleLinear()
      .domain([0, maxValue * 1.1])
      .range([this.height, 0])

    return { x, y, valueKey }
  }

  /**
   * Get the data value key based on the selected metric
   * @param {String} metric - The selected metric
   * @returns {String} - The key to use in data objects
   */
  getValueKeyForMetric(metric) {
    switch (metric) {
      case 'mouse':
        return 'mouseDistance'
      case 'keyboard':
        return 'keyPresses'
      default:
        return 'completionTime'
    }
  }

  /**
   * Update the axes based on the current scales
   * @param {Object} scales - The x and y scales
   */
  updateAxes({ x, y }) {
    // Update the x-axis
    this.chart
      .select('.x-axis')
      .transition()
      .duration(500)
      .call(
        d3
          .axisBottom(x)
          .ticks(Math.min(10, d3.max(x.domain())))
          .tickFormat(d3.format('d')),
      )

    // Format x-axis labels
    this.chart
      .select('.x-axis')
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)')

    // Update the y-axis
    this.chart.select('.y-axis').transition().duration(500).call(d3.axisLeft(y))
  }

  /**
   * Add horizontal grid lines to the chart
   * @param {d3.Scale} yScale - The y scale
   */
  addGridLines(yScale) {
    this.chart
      .selectAll('.grid-line-h')
      .data(yScale.ticks(5))
      .enter()
      .append('line')
      .attr('class', 'grid-line')
      .attr('x1', 0)
      .attr('x2', this.width)
      .attr('y1', d => yScale(d))
      .attr('y2', d => yScale(d))
      .attr('stroke', '#e0e0e0')
      .attr('stroke-dasharray', '3,3')
  }

  /**
   * Clear existing chart elements before redrawing
   */
  clearChartElements() {
    this.chart.selectAll('.line-path').remove()
    this.chart.selectAll('.data-point').remove()
    this.chart.selectAll('.grid-line').remove()
    this.chart.selectAll('.area-path').remove()
    this.chart.selectAll('.point-label').remove()
    this.chart.selectAll('defs').remove()
  }

  /**
   * Update the legend for individual tasks view
   * @param {Array} data - The task data
   * @param {String} metric - The selected metric
   * @param {d3.Scale} colorScale - The color scale
   */
  updateLegend(data, metric, colorScale) {
    // Determine prefix based on metric
    let displayNamePrefix = ''
    if (metric === 'mouse') displayNamePrefix = 'Mouse Movement: '
    if (metric === 'keyboard') displayNamePrefix = 'Key Presses: '

    // Update the legend
    const legend = this.chart.select('.legend')
    legend.selectAll('*').remove()

    // Add an entry for each task
    data.forEach((task, i) => {
      const legendItem = legend
        .append('g')
        .attr('transform', `translate(0, ${i * 20})`)

      legendItem
        .append('rect')
        .attr('width', 12)
        .attr('height', 12)
        .attr('fill', colorScale(i))

      legendItem
        .append('text')
        .attr('x', 18)
        .attr('y', 10)
        .text(`${displayNamePrefix}${task.taskName}`)
        .style('font-size', '12px')
    })
  }
}

export default ChartRenderer
