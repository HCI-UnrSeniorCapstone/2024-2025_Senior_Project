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
      <v-btn-toggle v-model="selectedView" mandatory>
        <v-btn small value="all" class="px-2">
          <v-icon x-small left>mdi-chart-line</v-icon>
          All Tasks
        </v-btn>
        <v-btn small value="individual" class="px-2">
          <v-icon x-small left>mdi-chart-multiple</v-icon>
          By Task
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
      chart: null,
      width: 0,
      height: 0,
      margin: { top: 40, right: 80, bottom: 110, left: 60 },
      resizeTimeout: null
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
    data() {
      this.updateChart();
    },
    // Watch for changes in selected participants
    selectedParticipantIds: {
      handler() {
        this.updateChart();
      },
      deep: true
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
      
      if (this.selectedView === 'all') {
        this.renderAllTasksView();
      } else {
        this.renderIndividualTasksView();
      }
    },
    
    // Render the "All Tasks" view (averaged data)
    renderAllTasksView() {
      const data = this.processedData;
      
      if (data.length === 0) return;
      
      // Set up scales
      const x = d3.scaleLinear()
        .domain([1, d3.max(data, d => d.attempt)])
        .range([0, this.width]);
      
      const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.completionTime) * 1.1])  // Add 10% padding at top
        .range([this.height, 0]);
      
      // Create the line generator
      const line = d3.line()
        .x(d => x(d.attempt))
        .y(d => y(d.completionTime))
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
      
      // Draw the line
      this.chart.append('path')
        .datum(data)
        .attr('class', 'line-path')
        .attr('fill', 'none')
        .attr('stroke', '#1976D2')
        .attr('stroke-width', 3)
        .attr('d', line);
      
      // Add data points
      this.chart.selectAll('.data-point')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'data-point')
        .attr('cx', d => x(d.attempt))
        .attr('cy', d => y(d.completionTime))
        .attr('r', 6)
        .attr('fill', '#1976D2')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2);
      
      // Add labels on the points
      this.chart.selectAll('.point-label')
        .data(data)
        .enter()
        .append('text')
        .attr('class', 'point-label')
        .attr('x', d => x(d.attempt))
        .attr('y', d => y(d.completionTime) - 15)
        .attr('text-anchor', 'middle')
        .text(d => `${Math.round(d.completionTime)}s`)
        .style('font-size', '11px')
        .style('fill', '#333');
      
      // Update the legend
      this.chart.select('.legend').selectAll('*').remove();
      
      const legend = this.chart.select('.legend');
      legend.append('rect')
        .attr('width', 15)
        .attr('height', 15)
        .attr('fill', '#1976D2');
      
      legend.append('text')
        .attr('x', 20)
        .attr('y', 12)
        .text('Average Completion Time')
        .style('font-size', '12px');
    },
    
    // Render the "Individual Tasks" view (separate lines)
    renderIndividualTasksView() {
      const data = this.processedData;
      
      if (data.length === 0) return;
      
      // Find max values for scales
      const maxAttempt = d3.max(data, d => d3.max(d.data, item => item.attempt));
      const maxTime = d3.max(data, d => d3.max(d.data, item => item.completionTime));
      
      // Set up scales
      const x = d3.scaleLinear()
        .domain([1, maxAttempt])
        .range([0, this.width]);
      
      const y = d3.scaleLinear()
        .domain([0, maxTime * 1.1])
        .range([this.height, 0]);
      
      // Use d3's built-in color scheme
      const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
      
      // Create the line generator
      const line = d3.line()
        .x(d => x(d.attempt))
        .y(d => y(d.completionTime))
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
        
        // Add the line
        this.chart.append('path')
          .datum(task.data)
          .attr('class', 'line-path')
          .attr('fill', 'none')
          .attr('stroke', color)
          .attr('stroke-width', 2.5)
          .attr('d', line);
        
        // Add data points
        this.chart.selectAll(`.data-point-${i}`)
          .data(task.data)
          .enter()
          .append('circle')
          .attr('class', 'data-point')
          .attr('cx', d => x(d.attempt))
          .attr('cy', d => y(d.completionTime))
          .attr('r', 5)
          .attr('fill', color)
          .attr('stroke', '#fff')
          .attr('stroke-width', 1.5);
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
          .text(task.taskName)
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
}
</style>