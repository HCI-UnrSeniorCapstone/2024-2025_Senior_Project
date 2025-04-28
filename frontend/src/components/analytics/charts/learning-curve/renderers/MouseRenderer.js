import * as d3 from 'd3'

/**
 * MouseRenderer handles the mouse-specific rendering for the Learning Curve Chart
 */
class MouseRenderer {
  /**
   * Render the "All Tasks" view with mouse metrics
   * @param {Object} options - Rendering options
   * @param {d3.Selection} options.chart - The chart selection
   * @param {Array} options.data - The processed data
   * @param {Object} options.scales - The x and y scales
   * @param {Number} options.height - The chart height
   */
  renderAllTasksView({ chart, data, scales, height }) {
    const { x, y, valueKey = 'mouseDistance' } = scales

    // Create gradient for mouse movement visualization
    const gradient = chart
      .append('defs')
      .append('linearGradient')
      .attr('id', 'mouse-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '0%')

    gradient.append('stop').attr('offset', '0%').attr('stop-color', '#FF5722')

    gradient.append('stop').attr('offset', '100%').attr('stop-color', '#FF9800')

    // Create the line generator
    const line = d3
      .line()
      .x(d => x(d.attempt))
      .y(d => y(d[valueKey]))
      .curve(d3.curveMonotoneX) // Smooth curve

    // Draw the line with curve and gradient
    chart
      .append('path')
      .datum(data)
      .attr('class', 'line-path')
      .attr('fill', 'none')
      .attr('stroke', 'url(#mouse-gradient)')
      .attr('stroke-width', 4)
      .attr('stroke-linecap', 'round')
      .attr('d', line)

    // Add area under the curve with low opacity
    const area = d3
      .area()
      .x(d => x(d.attempt))
      .y0(height)
      .y1(d => y(d[valueKey]))
      .curve(d3.curveMonotoneX)

    chart
      .append('path')
      .datum(data)
      .attr('class', 'area-path')
      .attr('fill', 'url(#mouse-gradient)')
      .attr('fill-opacity', 0.1)
      .attr('d', area)

    // Add data points
    chart
      .selectAll('.data-point')
      .data(data)
      .enter()
      .append('circle')
      .attr('class', 'data-point')
      .attr('cx', d => x(d.attempt))
      .attr('cy', d => y(d[valueKey]))
      .attr('r', 7) // Larger points for mouse
      .attr('fill', '#FF9800')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .attr('filter', 'drop-shadow(0px 1px 2px rgba(0,0,0,0.2))')

    // Add labels on the points
    chart
      .selectAll('.point-label')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'point-label')
      .attr('x', d => x(d.attempt))
      .attr('y', d => y(d[valueKey]) - 15)
      .attr('text-anchor', 'middle')
      .text(d => `${Math.round(d[valueKey])}px`)
      .style('font-size', '11px')
      .style('fill', '#333')

    // Update the legend
    const legend = chart.select('.legend')
    legend.selectAll('*').remove()

    legend
      .append('rect')
      .attr('width', 15)
      .attr('height', 15)
      .attr('fill', '#FF9800')

    legend
      .append('text')
      .attr('x', 20)
      .attr('y', 12)
      .text('Mouse Movement')
      .style('font-size', '12px')
  }

  /**
   * Render the "Individual Tasks" view with mouse metrics
   * @param {Object} options - Rendering options
   * @param {d3.Selection} options.chart - The chart selection
   * @param {Array} options.data - The processed data grouped by task
   * @param {Object} options.scales - The x and y scales
   * @param {d3.Scale} options.colorScale - The color scale for tasks
   * @param {Number} options.height - The chart height
   */
  renderIndividualTasksView({ chart, data, scales, colorScale, height }) {
    const { x, y, valueKey = 'mouseDistance' } = scales

    // Create the line generator
    const line = d3
      .line()
      .x(d => x(d.attempt))
      .y(d => y(d[valueKey]))
      .curve(d3.curveMonotoneX)

    // Create defs for gradients
    const defs = chart.append('defs')

    // Draw lines for each task
    data.forEach((task, i) => {
      const color = colorScale(i)

      // Create a gradient for this task
      const gradientId = `mouse-gradient-${i}`

      const gradient = defs
        .append('linearGradient')
        .attr('id', gradientId)
        .attr('x1', '0%')
        .attr('y1', '0%')
        .attr('x2', '0%')
        .attr('y2', '100%')

      gradient
        .append('stop')
        .attr('offset', '0%')
        .attr('stop-color', d3.rgb(color).darker(0.3))

      gradient.append('stop').attr('offset', '100%').attr('stop-color', color)

      // Add curved line with gradient
      chart
        .append('path')
        .datum(task.data)
        .attr('class', 'line-path')
        .attr('fill', 'none')
        .attr('stroke', `url(#${gradientId})`)
        .attr('stroke-width', 3)
        .attr('stroke-opacity', 0.8)
        .attr('stroke-linecap', 'round')
        .attr('d', line)

      // Add data points with glow effect
      chart
        .selectAll(`.data-point-${i}`)
        .data(task.data)
        .enter()
        .append('circle')
        .attr('class', 'data-point')
        .attr('cx', d => x(d.attempt))
        .attr('cy', d => y(d[valueKey]))
        .attr('r', 6)
        .attr('fill', color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5)
        .attr('filter', 'drop-shadow(0px 1px 1px rgba(0,0,0,0.2))')
    })
  }
}

export default MouseRenderer
