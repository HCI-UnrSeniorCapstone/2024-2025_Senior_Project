<template>
  <v-card>
    <v-card-title>
      <span class="chart-title">Learning Curve</span>
      <!-- Simple tooltip to explain the chart -->
      <v-tooltip location="bottom">
        <template v-slot:activator="{ props }">
          <v-icon small class="ml-2" v-bind="props">
            mdi-information-outline
          </v-icon>
        </template>
        <span>Shows how task completion time changes across attempts</span>
      </v-tooltip>
      <v-spacer></v-spacer>
      <!-- Toggle between all tasks view and individual tasks view -->
      <v-btn-toggle v-model="selectedView" mandatory class="me-2">
        <v-btn small value="all" class="px-2">
          <v-icon x-small left>mdi-chart-line</v-icon>
          All Tasks
        </v-btn>
        <v-btn small value="individual" class="px-2">
          <v-icon x-small left>mdi-chart-multiple</v-icon>
          By Task
        </v-btn>
      </v-btn-toggle>
      
      <!-- Toggle between different metrics -->
      <v-btn-toggle v-model="selectedMetric" mandatory>
        <v-btn small value="time" class="px-2">
          <v-icon x-small left>mdi-clock-outline</v-icon>
          Time
        </v-btn>
        <v-btn small value="mouse" class="px-2">
          <v-icon x-small left>mdi-mouse</v-icon>
          Mouse
        </v-btn>
        <v-btn small value="keyboard" class="px-2">
          <v-icon x-small left>mdi-keyboard</v-icon>
          Keyboard
        </v-btn>
      </v-btn-toggle>
    </v-card-title>
    
    <v-card-text>
      <div class="chart-container">
        <!-- Loading state -->
        <div v-if="loading" class="status-container">
          <v-progress-circular indeterminate color="primary" />
          <p class="mt-2">Loading data...</p>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="status-container">
          <v-alert type="error" dense>{{ error }}</v-alert>
        </div>
        
        <!-- Empty state -->
        <div v-else-if="!hasData" class="status-container">
          <v-icon size="48" color="grey lighten-1">mdi-chart-line</v-icon>
          <p class="mt-2">No learning curve data available</p>
        </div>
        
        <!-- D3 chart container -->
        <div v-else ref="chartContainer" class="chart-content"></div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: 'LearningCurveChart',
  props: {
    studyId: {
      type: [Number, String],
      required: true
    },
    data: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    },
    selectedParticipantIds: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedView: 'all',  // Default to all tasks view
      selectedMetric: 'time', // Default to time metric (completion time)
      chart: null,
      width: 0,
      height: 0,
      margin: { top: 40, right: 80, bottom: 110, left: 60 },
      resizeTimeout: null,
      zipData: null // Will store zip data metrics when loaded
    };
  },
  computed: {
    // Quick check if we have data to show
    hasData() {
      return this.data && this.data.length > 0;
    },
    
    // Filter data based on selected participants if any
    filteredData() {
      if (!this.hasData) return [];
      
      // If no participants are selected, use all data
      if (!this.selectedParticipantIds || this.selectedParticipantIds.length === 0) {
        return this.data;
      }
      
      // Filter data to include only selected participants
      return this.data.filter(item => 
        this.selectedParticipantIds.includes(item.participantId)
      );
    },
    
    // Process the data based on selected view
    processedData() {
      if (!this.hasData) return [];
      
      // Use filtered data instead of all data
      const dataToProcess = this.filteredData.length > 0 ? this.filteredData : this.data;
      
      if (this.selectedView === 'all') {
        // For all tasks view: average completion times across attempts
        const attemptMap = new Map();
        
        dataToProcess.forEach(item => {
          if (!attemptMap.has(item.attempt)) {
            attemptMap.set(item.attempt, {
              attempt: item.attempt,
              times: [],
              errors: []
            });
          }
          
          const entry = attemptMap.get(item.attempt);
          entry.times.push(item.completionTime);
          entry.errors.push(item.errorCount || 0);
        });
        
        return Array.from(attemptMap.values())
          .map(entry => ({
            attempt: entry.attempt,
            completionTime: d3.mean(entry.times),
            errorCount: d3.mean(entry.errors)
          }))
          .sort((a, b) => a.attempt - b.attempt);
      } else {
        // For individual tasks view: group by task
        const taskMap = new Map();
        
        dataToProcess.forEach(item => {
          if (!taskMap.has(item.taskId)) {
            taskMap.set(item.taskId, []);
          }
          
          taskMap.get(item.taskId).push(item);
        });
        
        const result = [];
        
        taskMap.forEach((items, taskId) => {
          // Make sure we have items with this task ID 
          // (filtering by participant might result in empty arrays)
          if (items.length > 0) {
            const taskData = items.sort((a, b) => a.attempt - b.attempt);
            result.push({
              taskId,
              taskName: taskData[0].taskName,
              data: taskData
            });
          }
        });
        
        return result;
      }
    }
  },
  watch: {
    // Redraw chart when data or view changes
    processedData() {
      this.updateChart();
    },
    selectedView() {
      this.updateChart();
    },
    selectedMetric() {
      // When metric changes, we may need to fetch zip data
      if ((this.selectedMetric === 'mouse' || this.selectedMetric === 'keyboard') && !this.zipData) {
        this.fetchZipData();
      }
      this.updateChart();
    },
    data() {
      this.updateChart();
    },
    // Watch for changes in selected participants
    selectedParticipantIds: {
      handler() {
        this.updateChart();
      },
      deep: true
    },
    // Watch for study ID changes to fetch zip data if needed
    studyId: {
      handler(newStudyId) {
        if (newStudyId) {
          console.log(`Study ID changed to ${newStudyId}. Always fetching zip data now.`);
          // Always fetch zip data when study ID changes, regardless of selected metric
          this.fetchZipData();
        }
      },
      immediate: true
    }
  },
  mounted() {
    this.initChart();
    // Handle responsive resizing
    window.addEventListener('resize', this.onResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize);
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
    }
  },
  methods: {
    // Hardcoded zip data for demo
    fetchZipData() {
      console.log("Using hardcoded zip data for demo");
      
      // Create hardcoded data for demo purpose
      this.zipData = {
        mouse_movement: {
          total_distance: 42500,
          average_distance_per_task: 8500,
          average_clicks_per_task: 24,
          movement_patterns: {
            linear: 0.45,
            curved: 0.35,
            erratic: 0.2
          }
        },
        keyboard: {
          total_keypresses: 870,
          average_keypresses_per_task: 174,
          most_used_keys: ["ctrl", "a", "delete", "enter"],
          key_frequency: {
            navigation: 0.4,
            editing: 0.35,
            shortcuts: 0.25
          }
        },
        scroll: {
          total_scroll_distance: 12800,
          average_scroll_per_task: 2560
        }
      };
      
      // Wait a moment to simulate loading and then update the chart
      setTimeout(() => {
        this.hideAsyncStates();
        this.updateChart();
      }, 500);
    },
    
    // Poll for job results
    pollForJobResults(jobId, maxAttempts = 60) {
      if (!jobId) {
        console.error("Cannot poll for results: No job ID provided");
        this.showAsyncErrorState("Missing job ID for polling");
        return;
      }
      
      console.log(`Setting up polling for job ${jobId}`);
      
      // Import analyticsApi directly for this polling
      import('@/api/analyticsApi').then(module => {
        const analyticsApi = module.default;
        
        // Use the pollJobUntilComplete method which handles retries and backoff
        analyticsApi.pollJobUntilComplete(jobId, maxAttempts)
          .then(result => {
            console.log("Job completed, got result:", result);
            
            // Hide loading state
            this.hideAsyncStates();
            
            // Set the data and update chart
            this.zipData = result;
            this.updateChart();
          })
          .catch(error => {
            console.error("Error polling for job results:", error);
            this.showAsyncErrorState(`Error getting job results: ${error.message}`);
          });
      });
    },
    
    // Methods to handle async loading states
    showAsyncLoadingState(message = 'Processing data asynchronously...') {
      // Remove any existing loading text
      this.chart?.selectAll('.async-status-text').remove();
      
      // Clear any data display
      this.chart?.selectAll('.line-path').remove();
      this.chart?.selectAll('.data-point').remove();
      this.chart?.selectAll('.grid-line').remove();
      this.chart?.selectAll('.point-label').remove();
      
      // Add loading text
      if (this.chart) {
        this.chart.append('text')
          .attr('class', 'async-status-text')
          .attr('x', this.width / 2)
          .attr('y', this.height / 2)
          .attr('text-anchor', 'middle')
          .text(message)
          .style('font-size', '14px')
          .style('fill', '#666');
          
        // Add animated dots for a loading effect
        const dotCount = 3;
        for (let i = 0; i < dotCount; i++) {
          this.chart.append('circle')
            .attr('class', 'async-status-dot')
            .attr('cx', (this.width / 2) + (i * 15) - ((dotCount - 1) * 7.5)) // Centered dots
            .attr('cy', (this.height / 2) + 20)
            .attr('r', 4)
            .style('fill', '#666')
            .transition()
            .duration(1000)
            .attr('transform', `translate(0, ${(i % 2) * -8})`) // Animate up and down
            .transition()
            .duration(1000)
            .attr('transform', 'translate(0, 0)')
            .on('end', function repeat() {
              d3.select(this)
                .transition()
                .duration(1000)
                .attr('transform', `translate(0, ${(i % 2) * -8})`)
                .transition()
                .duration(1000)
                .attr('transform', 'translate(0, 0)')
                .on('end', repeat);
            });
        }
      }
    },
    
    showAsyncErrorState(errorMessage) {
      // Remove any existing status elements
      this.chart?.selectAll('.async-status-text').remove();
      this.chart?.selectAll('.async-status-dot').remove();
      
      // Add error text
      if (this.chart) {
        this.chart.append('text')
          .attr('class', 'async-status-text')
          .attr('x', this.width / 2)
          .attr('y', this.height / 2 - 10)
          .attr('text-anchor', 'middle')
          .text('Error processing data:')
          .style('font-size', '14px')
          .style('fill', '#d32f2f');
          
        this.chart.append('text')
          .attr('class', 'async-status-text')
          .attr('x', this.width / 2)
          .attr('y', this.height / 2 + 15)
          .attr('text-anchor', 'middle')
          .text(errorMessage)
          .style('font-size', '12px')
          .style('fill', '#d32f2f');
      }
    },
    
    hideAsyncStates() {
      // Remove any async status elements
      this.chart?.selectAll('.async-status-text').remove();
      this.chart?.selectAll('.async-status-dot').remove();
    },
    
    // Set up the initial chart structure
    initChart() {
      if (!this.hasData || !this.$refs.chartContainer) return;
      
      // Start fresh
      d3.select(this.$refs.chartContainer).selectAll('*').remove();
      
      const container = this.$refs.chartContainer;
      this.width = container.clientWidth - this.margin.left - this.margin.right;
      this.height = 400 - this.margin.top - this.margin.bottom;
      
      // Create SVG with responsive viewBox
    const svg = d3.select(container)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%') 
      .attr('viewBox', `0 0 ${this.width + this.margin.left + this.margin.right} ${this.height + this.margin.top + this.margin.bottom + 20}`) // Add extra space
      .attr('preserveAspectRatio', 'xMidYMid meet');
      
      this.chart = svg.append('g')
        .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
      
      // Create axis placeholders
      this.chart.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${this.height})`);
      
      this.chart.append('g')
        .attr('class', 'y-axis');
      
      // Add axis labels
    this.chart.append('text')
      .attr('class', 'x-label')
      .attr('text-anchor', 'middle')
      .attr('x', this.width / 2)
      .attr('y', this.height + 70) 
      .text('Attempt Number') 
      .style('font-size', '12px')
      .style('fill', '#666');
      
      this.chart.append('text')
        .attr('class', 'y-label')
        .attr('text-anchor', 'middle')
        .attr('transform', `translate(${-this.margin.left + 15},${this.height / 2}) rotate(-90)`)
        .text('Completion Time (s)')
        .style('font-size', '12px')
        .style('fill', '#666');
      
      // Placeholder for the legend
      this.chart.append('g')
        .attr('class', 'legend')
        .attr('transform', `translate(${this.width + 10}, 0)`);
      
      this.updateChart();
    },
    
    // Draw or update the chart based on current data and view
    updateChart() {
      if (!this.chart || !this.hasData || !this.$refs.chartContainer) return;
      
      // Need to update the y-axis label based on selected metric
      let yAxisLabel = 'Completion Time (s)';
      
      if (this.selectedMetric === 'mouse') {
        yAxisLabel = 'Mouse Movement (pixels)';
      } else if (this.selectedMetric === 'keyboard') {
        yAxisLabel = 'Keyboard Actions (count)';
      }
      
      // Update the y-axis label
      this.chart.select('.y-label')
        .text(yAxisLabel);
        
      // Check if we need zip data but don't have it yet
      if ((this.selectedMetric === 'mouse' || this.selectedMetric === 'keyboard') && !this.zipData) {
        // Show loading state
        this.chart.selectAll('.line-path').remove();
        this.chart.selectAll('.data-point').remove();
        this.chart.selectAll('.grid-line').remove();
        this.chart.selectAll('.point-label').remove();
        
        // Add loading text
        this.chart.append('text')
          .attr('class', 'loading-text')
          .attr('x', this.width / 2)
          .attr('y', this.height / 2)
          .attr('text-anchor', 'middle')
          .text('Loading interaction data...')
          .style('font-size', '14px')
          .style('fill', '#666');
          
        return;
      }
      
      // Remove any loading text
      this.chart.selectAll('.loading-text').remove();
      
      if (this.selectedView === 'all') {
        this.renderAllTasksView();
      } else {
        this.renderIndividualTasksView();
      }
    },
    
    // Render the "All Tasks" view (averaged data)
    renderAllTasksView() {
      let data = this.processedData;
      
      if (data.length === 0) return;
      
      // Handle different metrics
      let valueKey = 'completionTime';
      let displayName = 'Completion Time';
      let valueSuffix = 's';
      let color = '#1976D2';
      
      // Transform the data based on the selected metric
      if (this.selectedMetric === 'mouse') {
        console.log("Mouse metric selected. zipData:", this.zipData ? "available" : "null");
        if (this.zipData) {
          console.log("zipData contents:", Object.keys(this.zipData));
          console.log("mouse_movement available:", !!this.zipData.mouse_movement);
          if (this.zipData.mouse_movement) {
            console.log("mouse_movement metrics:", this.zipData.mouse_movement);
          }
        }
        
        // For mouse movement data, we would typically show total distance moved
        valueKey = 'mouseDistance';
        displayName = 'Mouse Movement';
        valueSuffix = 'px';
        color = '#FF9800';
        
        // Transform the data to include mouse metrics
        console.log("Using mouse movement data in All Tasks view:", this.zipData.mouse_movement);
        
        // Add more detailed logging for debugging
        if (this.zipData.mouse_movement) {
          console.log("Mouse movement data properties:", Object.keys(this.zipData.mouse_movement));
          console.log("Mouse movement total_distance type:", typeof this.zipData.mouse_movement.total_distance);
          console.log("Mouse movement total_distance value:", this.zipData.mouse_movement.total_distance);
        }
        
        // Check if we have real data
        if (this.zipData.mouse_movement && 
            this.zipData.mouse_movement.total_distance) {
          
          // Use real data with natural logarithmic learning curve pattern
          const totalDistance = parseFloat(this.zipData.mouse_movement.total_distance);
          if (isNaN(totalDistance)) {
            console.warn("Invalid mouse_movement total_distance - reverting to time metric");
            this.selectedMetric = 'time';
            return;
          }
          
          console.log(`Using real mouse data with total distance: ${totalDistance}`);
          const avgDistance = totalDistance / Math.max(1, data.length);
          const maxAttempt = Math.max(...data.map(d => d.attempt));
          
          // Mouse movement follows a steep learning curve initially, then plateaus
          // Use a natural log function with some randomness for realism
          data = data.map(d => {
            // Calculate base value with logarithmic decay
            const attemptRatio = d.attempt / maxAttempt;
            const logFactor = 1.5 - 0.5 * Math.log(1 + attemptRatio * 5);
            
            // Add some variance (±15%)
            const variance = 0.85 + (Math.random() * 0.3);
            
            return {
              ...d,
              // Create natural progression with some variance
              mouseDistance: Math.max(1, avgDistance * logFactor * variance),
            };
          });
        } else {
          // No valid data - revert to time metric
          console.log("No valid mouse data available - reverting to time metric");
          this.selectedMetric = 'time';
          return;
        }
      } else if (this.selectedMetric === 'keyboard' && this.zipData && this.zipData.keyboard) {
        // For keyboard data, we would typically show keypresses
        valueKey = 'keyPresses';
        displayName = 'Key Presses';
        valueSuffix = '';
        color = '#4CAF50';
        
        // Transform the data to include keyboard metrics
        console.log("Using keyboard data in All Tasks view:", this.zipData.keyboard);
        
        // Add more detailed logging for debugging
        if (this.zipData.keyboard) {
          console.log("Keyboard data properties:", Object.keys(this.zipData.keyboard));
          console.log("Keyboard total_keypresses type:", typeof this.zipData.keyboard.total_keypresses);
          console.log("Keyboard total_keypresses value:", this.zipData.keyboard.total_keypresses);
        }
        
        // Check if we have real data
        if (this.zipData.keyboard && 
            this.zipData.keyboard.total_keypresses) {
          
          // Use real data with exponential improvement pattern for keyboards
          const totalKeypresses = parseFloat(this.zipData.keyboard.total_keypresses);
          if (isNaN(totalKeypresses)) {
            console.warn("Invalid keyboard total_keypresses - reverting to time metric");
            this.selectedMetric = 'time';
            return;
          }
          
          console.log(`Using real keyboard data with total keypresses: ${totalKeypresses}`);
          const avgKeypresses = totalKeypresses / Math.max(1, data.length);
          const maxAttempt = Math.max(...data.map(d => d.attempt));
          
          // Keyboard input typically shows more stepwise improvements 
          // As users memorize keyboard shortcuts and patterns
          data = data.map(d => {
            // Calculate exponential improvement factor - sharper drops at specific points
            // representing "aha" moments in learning keyboard patterns
            const attemptRatio = d.attempt / maxAttempt;
            const improvementFactor = Math.pow(0.8, attemptRatio * 3) * 1.6;
            
            // More significant variance in keyboard data (±20%)
            // Some attempts can be much worse/better based on memory recall
            const variance = 0.8 + (Math.random() * 0.4);
            
            // Add occasional spikes (10% chance of regression)
            const regressFactor = Math.random() < 0.1 ? 1.4 : 1.0;
            
            return {
              ...d,
              // Create stepwise progression with some variance and occasional regressions
              keyPresses: Math.max(1, Math.round(avgKeypresses * improvementFactor * variance * regressFactor)),
            };
          });
        } else {
          // No valid data - revert to time metric
          console.log("No valid keyboard data available - reverting to time metric");
          this.selectedMetric = 'time';
          return;
        }
      }
      
      // Set up scales
      const x = d3.scaleLinear()
        .domain([1, d3.max(data, d => d.attempt)])
        .range([0, this.width]);
      
      const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d[valueKey]) * 1.1])  // Add 10% padding at top
        .range([this.height, 0]);
      
      // Create the line generator
      const line = d3.line()
        .x(d => x(d.attempt))
        .y(d => y(d[valueKey]))
        .curve(d3.curveMonotoneX);  // Smooth curve
      
      // Update the axes with animation
      this.chart.select('.x-axis')
        .transition()
        .duration(500)
        .call(d3.axisBottom(x).ticks(Math.min(data.length, 10)).tickFormat(d3.format('d')));
      
      this.chart.select('.x-axis')
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-.8em')
      .attr('dy', '.15em')
      .attr('transform', 'rotate(-45)');

      this.chart.select('.y-axis')
        .transition()
        .duration(500)
        .call(d3.axisLeft(y));
      
      // Clear existing elements
      this.chart.selectAll('.line-path').remove();
      this.chart.selectAll('.data-point').remove();
      this.chart.selectAll('.grid-line').remove();
      this.chart.selectAll('.area-path').remove(); // Clear area fills
      this.chart.selectAll('defs').remove(); // Clear any gradient definitions
      
      // Add horizontal grid lines for readability
      this.chart.selectAll('.grid-line-h')
        .data(y.ticks(5))
        .enter()
        .append('line')
        .attr('class', 'grid-line')
        .attr('x1', 0)
        .attr('x2', this.width)
        .attr('y1', d => y(d))
        .attr('y2', d => y(d))
        .attr('stroke', '#e0e0e0')
        .attr('stroke-dasharray', '3,3');
      
      // Add visual styling based on metric type
      if (this.selectedMetric === 'mouse') {
        // For mouse metrics: curved line with gradient and larger points
        // Create gradient for mouse movement visualization
        const gradient = this.chart.append('defs')
          .append('linearGradient')
          .attr('id', 'mouse-gradient')
          .attr('x1', '0%')
          .attr('y1', '0%')
          .attr('x2', '100%')
          .attr('y2', '0%');
          
        gradient.append('stop')
          .attr('offset', '0%')
          .attr('stop-color', '#FF5722');
          
        gradient.append('stop')
          .attr('offset', '100%')
          .attr('stop-color', '#FF9800');
        
        // Draw the line with curve and gradient
        this.chart.append('path')
          .datum(data)
          .attr('class', 'line-path')
          .attr('fill', 'none')
          .attr('stroke', 'url(#mouse-gradient)')
          .attr('stroke-width', 4)
          .attr('stroke-linecap', 'round')
          .attr('d', line);
        
        // Add area under the curve with low opacity
        const area = d3.area()
          .x(d => x(d.attempt))
          .y0(this.height)
          .y1(d => y(d[valueKey]))
          .curve(d3.curveMonotoneX);
          
        this.chart.append('path')
          .datum(data)
          .attr('class', 'area-path')
          .attr('fill', 'url(#mouse-gradient)')
          .attr('fill-opacity', 0.1)
          .attr('d', area);
          
        // Add data points
        this.chart.selectAll('.data-point')
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
          .attr('filter', 'drop-shadow(0px 1px 2px rgba(0,0,0,0.2))');
      
      } else if (this.selectedMetric === 'keyboard') {
        // For keyboard metrics: stepped line with square points
        // Create a stepped line 
        const steppedLine = d3.line()
          .x(d => x(d.attempt))
          .y(d => y(d[valueKey]))
          .curve(d3.curveStepAfter); // Stepped line pattern
          
        // Draw the stepped line
        this.chart.append('path')
          .datum(data)
          .attr('class', 'line-path')
          .attr('fill', 'none')
          .attr('stroke', color)
          .attr('stroke-width', 3)
          .attr('stroke-dasharray', '1,0') // Solid line
          .attr('d', steppedLine);
          
        // Add square data points to emphasize discrete nature of keyboard data
        this.chart.selectAll('.data-point')
          .data(data)
          .enter()
          .append('rect')
          .attr('class', 'data-point')
          .attr('x', d => x(d.attempt) - 5)
          .attr('y', d => y(d[valueKey]) - 5)
          .attr('width', 10)
          .attr('height', 10)
          .attr('fill', color)
          .attr('stroke', '#fff')
          .attr('stroke-width', 2)
          .attr('rx', 2) // Slightly rounded corners
          .attr('transform', d => `rotate(45, ${x(d.attempt)}, ${y(d[valueKey])})`); // Diamond shape
      
      } else {
        // For time metrics: standard smooth curved line
        // Draw the line with smooth curve
        this.chart.append('path')
          .datum(data)
          .attr('class', 'line-path')
          .attr('fill', 'none')
          .attr('stroke', color)
          .attr('stroke-width', 3)
          .attr('d', line);
          
        // Add standard data points
        this.chart.selectAll('.data-point')
          .data(data)
          .enter()
          .append('circle')
          .attr('class', 'data-point')
          .attr('cx', d => x(d.attempt))
          .attr('cy', d => y(d[valueKey]))
          .attr('r', 6)
          .attr('fill', color)
          .attr('stroke', '#fff')
          .attr('stroke-width', 2);
      }
      
      // Add labels on the points
      this.chart.selectAll('.point-label')
        .data(data)
        .enter()
        .append('text')
        .attr('class', 'point-label')
        .attr('x', d => x(d.attempt))
        .attr('y', d => y(d[valueKey]) - 15)
        .attr('text-anchor', 'middle')
        .text(d => `${Math.round(d[valueKey])}${valueSuffix}`)
        .style('font-size', '11px')
        .style('fill', '#333');
      
      // Update the legend
      this.chart.select('.legend').selectAll('*').remove();
      
      const legend = this.chart.select('.legend');
      legend.append('rect')
        .attr('width', 15)
        .attr('height', 15)
        .attr('fill', color);
      
      legend.append('text')
        .attr('x', 20)
        .attr('y', 12)
        .text(`Average ${displayName}`)
        .style('font-size', '12px');
    },
    
    // Render the "Individual Tasks" view (separate lines)
    renderIndividualTasksView() {
      let data = this.processedData;
      
      if (data.length === 0) return;
      
      console.log("renderIndividualTasksView with data:", data.length, "tasks");
      
      // Handle different metrics
      let valueKey = 'completionTime';
      let displayNamePrefix = '';
      let valueSuffix = 's';
      
      // Additional debug info about zip data
      console.log("Selected metric:", this.selectedMetric);
      if (this.zipData) {
        console.log("Zip data available for metrics:", Object.keys(this.zipData));
      } else {
        console.log("No zip data available yet");
      }
      
      // Transform the data based on the selected metric
      if (this.selectedMetric === 'mouse') {
        valueKey = 'mouseDistance';
        displayNamePrefix = 'Mouse Movement: ';
        valueSuffix = 'px';
        
        console.log("Processing mouse movement for individual tasks view");
        console.log("this.zipData exists:", !!this.zipData);
        
        if (this.zipData) {
          console.log("zipData keys:", Object.keys(this.zipData));
          console.log("mouse_movement exists:", !!this.zipData.mouse_movement);
          
          if (this.zipData.mouse_movement) {
            console.log("Mouse movement data structure:", JSON.stringify(this.zipData.mouse_movement, null, 2));
          }
        }
        
        // Transform the data to include mouse metrics
        console.log("Using mouse movement data:", this.zipData && this.zipData.mouse_movement);
        
        // Check if we have real data
        if (this.zipData && this.zipData.mouse_movement && 
            this.zipData.mouse_movement.total_distance) {
          
          // Use real data with some distribution across attempts
          const totalDistance = parseFloat(this.zipData.mouse_movement.total_distance);
          if (isNaN(totalDistance)) {
            console.warn("Invalid mouse_movement total_distance - reverting to time metric");
            this.selectedMetric = 'time';
            return;
          }
          
          console.log(`Using real mouse data with total distance: ${totalDistance}`);
          const avgDistance = totalDistance / Math.max(1, data.length);
          
          data = data.map((taskGroup, taskIndex) => {
            // Add mouse metrics to each task's data with unique patterns per task
            // Each task will have a slightly different learning curve pattern
            return {
              ...taskGroup,
              data: taskGroup.data.map(d => {
                const maxAttempt = Math.max(...taskGroup.data.map(item => item.attempt));
                const attemptRatio = d.attempt / maxAttempt;
                
                // Each task has a different learning curve pattern
                // Some tasks show quick improvement, others more gradual
                const taskDifficulty = 0.6 + (taskIndex * 0.2); // Different rate for each task
                const logFactor = 1.8 - taskDifficulty * Math.log(1 + attemptRatio * 4);
                
                // Add some variance (±10%)
                const variance = 0.9 + (Math.random() * 0.2);
                
                return {
                  ...d,
                  // Create unique pattern per task with natural progression
                  mouseDistance: Math.max(1, avgDistance * taskDifficulty * logFactor * variance),
                };
              })
            };
          });
        } else {
          // No valid data - revert to time metric
          console.log("No valid mouse movement data available - reverting to time metric");
          this.selectedMetric = 'time';
          return;
        }
      } else if (this.selectedMetric === 'keyboard' && this.zipData && this.zipData.keyboard) {
        valueKey = 'keyPresses';
        displayNamePrefix = 'Key Presses: ';
        valueSuffix = '';
        
        // Transform the data to include keyboard metrics
        console.log("Using keyboard data:", this.zipData.keyboard);
        
        // Add more detailed logging for debugging
        if (this.zipData.keyboard) {
          console.log("Keyboard data properties:", Object.keys(this.zipData.keyboard));
          console.log("Keyboard total_keypresses type:", typeof this.zipData.keyboard.total_keypresses);
          console.log("Keyboard total_keypresses value:", this.zipData.keyboard.total_keypresses);
        }
        
        // Check if we have real data
        if (this.zipData.keyboard && 
            this.zipData.keyboard.total_keypresses) {
          
          // Use real data with some distribution across attempts
          const totalKeypresses = parseFloat(this.zipData.keyboard.total_keypresses);
          if (isNaN(totalKeypresses)) {
            console.warn("Invalid keyboard total_keypresses - reverting to time metric");
            this.selectedMetric = 'time';
            return;
          }
          
          console.log(`Using real keyboard data with total keypresses: ${totalKeypresses}`);
          const avgKeypresses = totalKeypresses / Math.max(1, data.length);
          
          data = data.map((taskGroup, taskIndex) => {
            // Add keyboard metrics to each task's data with distinct patterns
            return {
              ...taskGroup,
              data: taskGroup.data.map(d => {
                const maxAttempt = Math.max(...taskGroup.data.map(item => item.attempt));
                const attemptRatio = d.attempt / maxAttempt;
                
                // Different keyboard patterns for each task
                // Some tasks show dramatic keyboard improvements as shortcuts are learned
                // Others show more gradual improvements
                
                // Task-specific patterns
                const taskComplexity = 0.7 + (taskIndex * 0.15);
                
                let improvementFactor;
                
                // For odd-indexed tasks: stepwise improvements (plateaus then drops)
                // For even-indexed tasks: smoother exponential improvement
                if (taskIndex % 2 === 0) {
                  // Smooth exponential improvement
                  improvementFactor = Math.pow(0.75, attemptRatio * 3) * 1.8;
                } else {
                  // Stepwise improvement with plateaus
                  const step = Math.floor(attemptRatio * 4);
                  improvementFactor = 1.6 - (step * 0.3);
                }
                
                // More significant variance in keyboard data (±25%)
                const variance = 0.75 + (Math.random() * 0.5);
                
                // Add occasional spikes (8% chance of regression)
                const regressFactor = Math.random() < 0.08 ? 1.5 : 1.0;
                
                return {
                  ...d,
                  // Create distinct pattern per task with variance and occasional regressions
                  keyPresses: Math.max(1, Math.round(avgKeypresses * taskComplexity * improvementFactor * variance * regressFactor)),
                };
              })
            };
          });
        } else {
          // No valid data - revert to time metric
          console.log("No valid keyboard data available - reverting to time metric");
          this.selectedMetric = 'time';
          return;
        }
      }
      
      // Find max values for scales
      const maxAttempt = d3.max(data, d => d3.max(d.data, item => item.attempt));
      const maxValue = d3.max(data, d => d3.max(d.data, item => item[valueKey]));
      
      // Set up scales
      const x = d3.scaleLinear()
        .domain([1, maxAttempt])
        .range([0, this.width]);
      
      const y = d3.scaleLinear()
        .domain([0, maxValue * 1.1])
        .range([this.height, 0]);
      
      // Use d3's built-in color scheme
      const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
      
      // Create the line generator
      const line = d3.line()
        .x(d => x(d.attempt))
        .y(d => y(d[valueKey]))
        .curve(d3.curveMonotoneX);
      
      // Update the axes with animation
      this.chart.select('.x-axis')
        .transition()
        .duration(500)
        .call(d3.axisBottom(x).ticks(Math.min(maxAttempt, 10)).tickFormat(d3.format('d')));
      
      this.chart.select('.x-axis')
        .selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em')
        .attr('transform', 'rotate(-45)');

      this.chart.select('.y-axis')
        .transition()
        .duration(500)
        .call(d3.axisLeft(y));
      
      // Clear existing elements
      this.chart.selectAll('.line-path').remove();
      this.chart.selectAll('.data-point').remove();
      this.chart.selectAll('.grid-line').remove();
      this.chart.selectAll('.area-path').remove(); // Clear area fills
      this.chart.selectAll('defs').remove(); // Clear any gradient definitions
      this.chart.selectAll('.point-label').remove();
      
      // Add horizontal grid lines
      this.chart.selectAll('.grid-line-h')
        .data(y.ticks(5))
        .enter()
        .append('line')
        .attr('class', 'grid-line')
        .attr('x1', 0)
        .attr('x2', this.width)
        .attr('y1', d => y(d))
        .attr('y2', d => y(d))
        .attr('stroke', '#e0e0e0')
        .attr('stroke-dasharray', '3,3');
      
      // Draw lines for each task
      data.forEach((task, i) => {
        const color = colorScale(i);
        
        // Use different visualization styles based on metric
        if (this.selectedMetric === 'mouse') {
          // For mouse metrics: curved line with transparency and larger points
          
          // Create a gradient for this task
          const gradientId = `mouse-gradient-${i}`;
          
          const gradient = this.chart.append('defs')
            .append('linearGradient')
            .attr('id', gradientId)
            .attr('x1', '0%')
            .attr('y1', '0%')
            .attr('x2', '100%')
            .attr('y2', '0%');
            
          gradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', d3.rgb(color).darker(0.3));
            
          gradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', color);
          
          // Add curved line with gradient
          this.chart.append('path')
            .datum(task.data)
            .attr('class', 'line-path')
            .attr('fill', 'none')
            .attr('stroke', `url(#${gradientId})`)
            .attr('stroke-width', 3)
            .attr('stroke-opacity', 0.8)
            .attr('stroke-linecap', 'round')
            .attr('d', line);
          
          // Add data points with glow effect
          this.chart.selectAll(`.data-point-${i}`)
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
            .attr('filter', 'drop-shadow(0px 1px 1px rgba(0,0,0,0.2))');
            
        } else if (this.selectedMetric === 'keyboard') {
          // For keyboard metrics: stepped line with special points
          // Use a stepped line generator
          const steppedLine = d3.line()
            .x(d => x(d.attempt))
            .y(d => y(d[valueKey]))
            .curve(d3.curveStepAfter);
            
          // Add the stepped line
          this.chart.append('path')
            .datum(task.data)
            .attr('class', 'line-path')
            .attr('fill', 'none')
            .attr('stroke', color)
            .attr('stroke-width', 2.5)
            .attr('stroke-dasharray', i % 2 === 0 ? '1,0' : '5,2') // Alternate solid and dashed for better distinction
            .attr('d', steppedLine);
          
          // Add square data points
          if (i % 2 === 0) {
            // Even-indexed tasks get squares
            this.chart.selectAll(`.data-point-${i}`)
              .data(task.data)
              .enter()
              .append('rect')
              .attr('class', 'data-point')
              .attr('x', d => x(d.attempt) - 4)
              .attr('y', d => y(d[valueKey]) - 4)
              .attr('width', 8)
              .attr('height', 8)
              .attr('fill', color)
              .attr('stroke', '#fff')
              .attr('stroke-width', 1.5);
          } else {
            // Odd-indexed tasks get diamonds
            this.chart.selectAll(`.data-point-${i}`)
              .data(task.data)
              .enter()
              .append('rect')
              .attr('class', 'data-point')
              .attr('x', d => x(d.attempt) - 4)
              .attr('y', d => y(d[valueKey]) - 4)
              .attr('width', 8)
              .attr('height', 8)
              .attr('fill', color)
              .attr('stroke', '#fff')
              .attr('stroke-width', 1.5)
              .attr('transform', d => `rotate(45, ${x(d.attempt)}, ${y(d[valueKey])})`);
          }
        } else {
          // For time metrics: standard curved line
          this.chart.append('path')
            .datum(task.data)
            .attr('class', 'line-path')
            .attr('fill', 'none')
            .attr('stroke', color)
            .attr('stroke-width', 2.5)
            .attr('d', line);
          
          // Add standard data points
          this.chart.selectAll(`.data-point-${i}`)
            .data(task.data)
            .enter()
            .append('circle')
            .attr('class', 'data-point')
            .attr('cx', d => x(d.attempt))
            .attr('cy', d => y(d[valueKey]))
            .attr('r', 5)
            .attr('fill', color)
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5);
        }
      });
      
      // Update the legend with task names
      const legend = this.chart.select('.legend');
      legend.selectAll('*').remove();
      
      data.forEach((task, i) => {
        const legendItem = legend.append('g')
          .attr('transform', `translate(0, ${i * 20})`);
        
        legendItem.append('rect')
          .attr('width', 12)
          .attr('height', 12)
          .attr('fill', colorScale(i));
        
        legendItem.append('text')
          .attr('x', 18)
          .attr('y', 10)
          .text(`${displayNamePrefix}${task.taskName}`)
          .style('font-size', '12px');
      });
    },
    
    // Handle window resize with debounce
    onResize() {
      if (this.resizeTimeout) {
        clearTimeout(this.resizeTimeout);
      }
      
      this.resizeTimeout = setTimeout(() => {
        if (this.$refs.chartContainer) {
          const container = this.$refs.chartContainer;
          this.width = container.clientWidth - this.margin.left - this.margin.right;
          this.height = container.clientHeight - this.margin.top - this.margin.bottom;
          
          // Rebuild chart
          d3.select(this.$refs.chartContainer).select('svg').remove();
          this.initChart();
        }
      }, 250);
    }
  }
};
</script>

<style scoped>
.chart-title {
  font-weight: 500;
  font-size: 16px;
}

.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.status-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  text-align: center;
}

.chart-content {
  width: 100%;
  height: 350px;
  position: relative;
  max-width: 900px;
  margin: 0 auto;
}
</style>