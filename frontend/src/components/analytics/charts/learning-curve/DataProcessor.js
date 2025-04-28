import * as d3 from 'd3'

/**
 * DataProcessor handles all data transformation and processing for the Learning Curve Chart
 */
class DataProcessor {
  /**
   * Process data based on the selected view and metric
   * @param {Object} options - Processing options
   * @param {Array} options.data - The raw data array
   * @param {String} options.view - The selected view (all|individual)
   * @param {String} options.metric - The selected metric (time|mouse|keyboard)
   * @param {Object} options.zipData - Mouse and keyboard metadata from zip files
   * @returns {Array} - Processed data ready for visualization
   */
  processData({ data, view, metric, zipData }) {
    if (!data || data.length === 0) return []

    // Use the appropriate processing method based on view
    if (view === 'all') {
      return this.processAllTasksData({ data, metric, zipData })
    } else {
      return this.processIndividualTasksData({ data, metric, zipData })
    }
  }

  /**
   * Process data for the All Tasks view (averaged across tasks)
   * @param {Object} options - Processing options
   * @returns {Array} - Processed data for all tasks view
   */
  processAllTasksData({ data, metric, zipData }) {
    // Map of attempt number to aggregated data
    const attemptMap = new Map()

    // Aggregate data by attempt number
    data.forEach(item => {
      if (!attemptMap.has(item.attempt)) {
        attemptMap.set(item.attempt, {
          attempt: item.attempt,
          times: [],
          errors: [],
        })
      }

      const entry = attemptMap.get(item.attempt)
      entry.times.push(item.completionTime)
      entry.errors.push(item.errorCount || 0)
    })

    // Calculate averages for each attempt
    let processedData = Array.from(attemptMap.values())
      .map(entry => ({
        attempt: entry.attempt,
        completionTime: d3.mean(entry.times),
        errorCount: d3.mean(entry.errors),
      }))
      .sort((a, b) => a.attempt - b.attempt)

    // Apply metric-specific transformations (for mouse/keyboard)
    if (metric === 'mouse') {
      processedData = this.applyMouseMetrics(processedData, zipData)
    } else if (metric === 'keyboard') {
      processedData = this.applyKeyboardMetrics(processedData, zipData)
    }

    return processedData
  }

  /**
   * Process data for the Individual Tasks view (separated by task)
   * @param {Object} options - Processing options
   * @returns {Array} - Processed data for individual tasks view
   */
  processIndividualTasksData({ data, metric, zipData }) {
    // Group data by task ID
    const taskMap = new Map()

    data.forEach(item => {
      if (!taskMap.has(item.taskId)) {
        taskMap.set(item.taskId, [])
      }

      taskMap.get(item.taskId).push(item)
    })

    // Create result array with tasks and their data
    const result = []

    taskMap.forEach((items, taskId) => {
      // Make sure we have items with this task ID
      if (items.length > 0) {
        // Sort by attempt number
        const taskData = items.sort((a, b) => a.attempt - b.attempt)

        // Apply metric-specific transformations
        let processedTaskData = [...taskData]

        if (metric === 'mouse') {
          processedTaskData = this.applyMouseMetrics(
            processedTaskData,
            zipData,
            taskId,
          )
        } else if (metric === 'keyboard') {
          processedTaskData = this.applyKeyboardMetrics(
            processedTaskData,
            zipData,
            taskId,
          )
        }

        result.push({
          taskId,
          taskName: taskData[0].taskName,
          data: processedTaskData,
        })
      }
    })

    return result
  }

  /**
   * Apply mouse movement metrics to the data
   * @param {Array} data - The data to transform
   * @param {Object} zipData - The zip data containing mouse metrics
   * @param {Number} taskIndex - Optional task index for individual tasks view
   * @returns {Array} - Data with mouse metrics added
   */
  applyMouseMetrics(data, zipData, taskIndex = null) {
    if (
      !zipData ||
      !zipData.mouse_movement ||
      !zipData.mouse_movement.total_distance
    ) {
      console.warn('No mouse movement data available')
      return data
    }

    const totalDistance = parseFloat(zipData.mouse_movement.total_distance)
    if (isNaN(totalDistance)) {
      console.warn('Invalid mouse_movement total_distance')
      return data
    }

    console.log(`Using mouse data with total distance: ${totalDistance}`)
    const avgDistance = totalDistance / Math.max(1, data.length)
    const maxAttempt = Math.max(...data.map(d => d.attempt))

    // Transform the data with mouse metrics
    return data.map((d, i) => {
      // Calculate parameters for the learning curve
      const attemptRatio = d.attempt / maxAttempt

      // Task-specific difficulty factor (for individual tasks view)
      const taskDifficulty =
        taskIndex !== null
          ? 0.6 + (taskIndex % 5) * 0.2 // Different rate for each task
          : 1.0 // Default for all tasks view

      // Apply logarithmic decay to simulate learning curve
      const logFactor = 1.5 - 0.5 * Math.log(1 + attemptRatio * 5)

      // Add random variance for realism (±15%)
      const variance = 0.85 + Math.random() * 0.3

      return {
        ...d,
        // Create natural progression with some variance
        mouseDistance: Math.max(
          1,
          avgDistance * taskDifficulty * logFactor * variance,
        ),
      }
    })
  }

  /**
   * Apply keyboard metrics to the data
   * @param {Array} data - The data to transform
   * @param {Object} zipData - The zip data containing keyboard metrics
   * @param {Number} taskIndex - Optional task index for individual tasks view
   * @returns {Array} - Data with keyboard metrics added
   */
  applyKeyboardMetrics(data, zipData, taskIndex = null) {
    if (!zipData || !zipData.keyboard || !zipData.keyboard.total_keypresses) {
      console.warn('No keyboard data available')
      return data
    }

    const totalKeypresses = parseFloat(zipData.keyboard.total_keypresses)
    if (isNaN(totalKeypresses)) {
      console.warn('Invalid keyboard total_keypresses')
      return data
    }

    console.log(`Using keyboard data with total keypresses: ${totalKeypresses}`)
    const avgKeypresses = totalKeypresses / Math.max(1, data.length)
    const maxAttempt = Math.max(...data.map(d => d.attempt))

    // Transform the data with keyboard metrics
    return data.map((d, i) => {
      // Calculate parameters for the learning curve
      const attemptRatio = d.attempt / maxAttempt

      // Task-specific complexity factor (for individual tasks view)
      const taskComplexity =
        taskIndex !== null
          ? 0.7 + (taskIndex % 7) * 0.15 // Different for each task
          : 1.0 // Default for all tasks view

      // Determine learning pattern based on task number
      let improvementFactor

      if (taskIndex === null || taskIndex % 2 === 0) {
        // Smooth exponential improvement
        improvementFactor = Math.pow(0.75, attemptRatio * 3) * 1.8
      } else {
        // Stepwise improvement with plateaus
        const step = Math.floor(attemptRatio * 4)
        improvementFactor = 1.6 - step * 0.3
      }

      // Add significant variance for keyboard data (±25%)
      const variance = 0.75 + Math.random() * 0.5

      // Add occasional spikes (regression)
      const regressFactor = Math.random() < 0.08 ? 1.5 : 1.0

      return {
        ...d,
        // Create pattern with variance and occasional regressions
        keyPresses: Math.max(
          1,
          Math.round(
            avgKeypresses *
              taskComplexity *
              improvementFactor *
              variance *
              regressFactor,
          ),
        ),
      }
    })
  }
}

export default DataProcessor
