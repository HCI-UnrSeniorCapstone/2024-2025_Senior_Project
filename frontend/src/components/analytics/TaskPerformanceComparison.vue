<template>
  <v-card>
    <v-card-title>
      <span class="chart-title">Task Performance Comparison</span>
      <!-- Tooltip for chart explanation -->
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-icon small class="ml-2" v-bind="attrs" v-on="on">
            mdi-information-outline
          </v-icon>
        </template>
        <span>Compares performance metrics across different tasks</span>
      </v-tooltip>
      <v-spacer></v-spacer>
      <!-- Toggle between different metrics -->
      <v-btn-toggle v-model="selectedMetric" mandatory>
        <v-btn small value="time" class="px-2">
          <v-icon x-small left>mdi-clock-outline</v-icon>
          Time
        </v-btn>
        <v-btn small value="success" class="px-2">
          <v-icon x-small left>mdi-check-circle-outline</v-icon>
          Success
        </v-btn>
        <v-btn small value="errors" class="px-2">
          <v-icon x-small left>mdi-alert-circle-outline</v-icon>
          Errors
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
          <v-icon size="48" color="grey lighten-1">mdi-chart-bar</v-icon>
          <p class="mt-2">No task performance data available</p>
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
  name: 'TaskPerformanceComparison',
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
    }
  },
  data() {
    return {
      selectedMetric: 'time',  // Default selected metric
      chart: null,
      width: 0,
      height: 0,
      margin: { top: 40, right: 80, bottom: 120, left: 60 }, 
      resizeTimeout: null
    };
  },
  computed: {
    // Check if we have data to display
    hasData() {
      return this.data && this.data.length > 0;
    },
    
    // Get the appropriate label based on selected metric
    metricLabel() {
      switch (this.selectedMetric) {
        case 'time':
          return 'Avg Time (s)';
        case 'success':
          return 'Success Rate (%)';
        case 'errors':
          return 'Error Rate';
      }
    },
    
    // Color scheme for the selected metric
    metricColor() {
      switch (this.selectedMetric) {
        case 'time':
          return '#1976D2';  // Blue
        case 'success':
          return '#4CAF50';  // Green
        case 'errors':
          return '#FFC107';  // Amber/yellow
      }
    }
  },
  watch: {
    // Redraw when data changes
    data() {
      this.updateChart();
    },
    // Update chart when metric changes
    selectedMetric() {
      this.updateChart();
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
    // Extract the appropriate value based on selected metric
    getMetricValue(task) {
      switch (this.selectedMetric) {
        case 'time':
          return task.avgCompletionTime;
        case 'success':
          return task.successRate;
        case 'errors':
          return task.errorRate;
      }
      return 0;
    },
    
    // Format the value for display based on metric type
    formatValue(value) {
      switch (this.selectedMetric) {
        case 'time':
          return `${value.toFixed(1)}s`;
        case 'success':
          return `${value.toFixed(1)}%`;
        case 'errors':
          return value.toFixed(2);
      }
      return value;
    },
    
    // Set up initial chart structure and containers
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
      .attr('height', '100%') // Change from fixed 400px
      .attr('viewBox', `0 0 ${this.width + this.margin.left + this.margin.right} ${this.height + this.margin.top + this.margin.bottom}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');

      this.chart = svg.append('g')
        .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
      
      // Create axis placeholders
      this.chart.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${this.height})`);
      
      this.chart.append('g')
        .attr('class', 'y-axis');
      
      // Add y-axis label
      this.chart.append('text')
        .attr('class', 'y-label')
        .attr('text-anchor', 'middle')
        .attr('transform', `translate(${-this.margin.left + 15},${this.height / 2}) rotate(-90)`)
        .style('font-size', '12px')
        .style('fill', '#666');
      
      this.updateChart();
    },
    
    // Draw or update the chart based on current data and metric
    updateChart() {
      if (!this.chart || !this.hasData || !this.$refs.chartContainer) return;
      
      // Sort data by the selected metric
      const data = [...this.data].sort((a, b) => this.getMetricValue(a) - this.getMetricValue(b));
      
      // Set up x-scale for bar chart
      const x = d3.scaleBand()
        .domain(data.map(d => d.taskId))
        .range([0, this.width])
        .padding(0.3);
      
      // Determine y-scale domain based on metric
      let yMin = 0;
      let yMax;
      
      switch (this.selectedMetric) {
        case 'time':
          yMax = d3.max(data, d => d.avgCompletionTime) * 1.1;  // Add 10% padding
          break;
        case 'success':
          yMax = 100;  // Success rate is always 0-100%
          break;
        case 'errors':
          yMax = d3.max(data, d => d.errorRate) * 1.1;
          break;
      }
      
      const y = d3.scaleLinear()
        .domain([0, yMax*1.2])
        .range([this.height, 0])
        .nice();
      
      // Update x-axis with task names
      const xAxis = this.chart.select('.x-axis')
        .transition()
        .duration(500)
        .call(d3.axisBottom(x)
          .tickFormat(taskId => {
            const task = data.find(d => d.taskId === taskId);
            if (!task) return '';
            
            let taskName = task.taskName;
            
            // Remove trailing "task" 
            taskName = taskName.replace(/\s+task$/i, '');
            
            // Remove any double spaces left
            taskName = taskName.replace(/\s{2,}/g, ' ').trim();
            
            return taskName;
          }));
      
      // Rotate labels to prevent overlap
      xAxis.selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-0.5em')  
        .attr('dy', '0.15em')  
        .attr('transform', 'rotate(-35)')  
        .style('font-size', '11px')  
        .style('font-weight', '500');
      
      this.chart.select('.y-axis')
        .transition()
        .duration(500)
        .call(d3.axisLeft(y));
      
      // Update y-axis label
      this.chart.select('.y-label')
        .text(this.metricLabel);
      
      // Add horizontal grid lines
      this.chart.selectAll('.grid-line').remove();
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
      
      // Clean up before redrawing
      this.chart.selectAll('.bar').remove();
      this.chart.selectAll('.bar-label').remove();
      
      // Add bars with animation
      const bars = this.chart.selectAll('.bar')
        .data(data)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.taskId))
        .attr('width', x.bandwidth())
        .attr('y', this.height)  // Start at bottom for animation
        .attr('height', 0)
        .attr('fill', this.metricColor)
        .attr('rx', 2)  // Rounded corners
        .attr('ry', 2);
      
      // Animate bars growing upward
      bars.transition()
        .duration(800)
        .delay((d, i) => i * 100)  // Stagger animation
        .attr('y', d => y(this.getMetricValue(d)))
        .attr('height', d => this.height - y(this.getMetricValue(d)));
      
      // Add hover effects
      bars.on('mouseover', function() {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('opacity', 0.8);
        })
        .on('mouseout', function() {
          d3.select(this)
            .transition()
            .duration(200)
            .attr('opacity', 1);
        });
      
      // Add value labels above bars
      this.chart.selectAll('.bar-label')
        .data(data)
        .enter()
        .append('text')
        .attr('class', 'bar-label')
        .attr('x', d => x(d.taskId) + x.bandwidth() / 2)
        .attr('y', d => y(this.getMetricValue(d)) - 5)
        .attr('text-anchor', 'middle')
        .style('font-size', '11px')
        .style('fill', '#333')
        .style('opacity', 0)  // Start invisible for animation
        .text(d => this.formatValue(this.getMetricValue(d)))
        .transition()
        .duration(800)
        .delay((d, i) => 300 + i * 100)  // Appear after bars
        .style('opacity', 1);
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