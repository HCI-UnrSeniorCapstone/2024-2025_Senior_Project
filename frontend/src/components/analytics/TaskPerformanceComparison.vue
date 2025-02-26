<template>
  <v-card>
    <v-card-title>
      <span>Task Performance Comparison</span>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-icon small class="ml-2" v-bind="attrs" v-on="on">
            mdi-information-outline
          </v-icon>
        </template>
        <span>Compares performance metrics across different tasks</span>
      </v-tooltip>
      <v-spacer></v-spacer>
      <v-btn-toggle v-model="selectedMetric" mandatory>
        <v-btn small value="time">Time</v-btn>
        <v-btn small value="success">Success</v-btn>
        <v-btn small value="errors">Errors</v-btn>
      </v-btn-toggle>
    </v-card-title>
    <v-card-text>
      <div v-if="loading" class="loading-container">
        <v-progress-circular indeterminate color="primary" />
        <p class="mt-2">Loading data...</p>
      </div>
      <div v-else-if="error" class="error-container">
        <v-alert type="error" dense>{{ error }}</v-alert>
      </div>
      <div v-else-if="!hasData" class="empty-container">
        <p>No task performance data available</p>
      </div>
      <div v-else>
        <div ref="chartContainer" class="chart-container"></div>
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
      selectedMetric: 'time',
      chart: null,
      width: 0,
      height: 0,
      margin: { top: 20, right: 20, bottom: 80, left: 60 }
    };
  },
  computed: {
    hasData() {
      return this.data && this.data.length > 0;
    },
    metricLabel() {
      switch (this.selectedMetric) {
        case 'time':
          return 'Avg Time (s)';
        case 'success':
          return 'Success Rate (%)';
        case 'errors':
          return 'Error Rate';
      }
    }
  },
  watch: {
    data() {
      this.updateChart();
    },
    selectedMetric() {
      this.updateChart();
    }
  },
  mounted() {
    this.initChart();
    window.addEventListener('resize', this.onResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize);
  },
  methods: {
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
    
    initChart() {
      if (!this.hasData) return;
      
      const container = this.$refs.chartContainer;
      if (!container) return;
      
      this.width = container.clientWidth - this.margin.left - this.margin.right;
      this.height = 400 - this.margin.top - this.margin.bottom;
      
      const svg = d3.select(container).append('svg')
        .attr('width', '100%')
        .attr('height', 400)
        .attr('viewBox', `0 0 ${this.width + this.margin.left + this.margin.right} ${this.height + this.margin.top + this.margin.bottom}`)
        .attr('preserveAspectRatio', 'xMidYMid meet');
      
      this.chart = svg.append('g')
        .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
      
      // Add axes groups
      this.chart.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0,${this.height})`);
      
      this.chart.append('g')
        .attr('class', 'y-axis');
      
      // Add y-axis label
      this.chart.append('text')
        .attr('class', 'y-label')
        .attr('text-anchor', 'middle')
        .attr('transform', `translate(${-this.margin.left + 15},${this.height / 2}) rotate(-90)`);
      
      this.updateChart();
    },
    
    updateChart() {
      if (!this.chart || !this.hasData) return;
      
      const data = [...this.data].sort((a, b) => this.getMetricValue(a) - this.getMetricValue(b));
      
      // Set up scales
      const x = d3.scaleBand()
        .domain(data.map(d => d.taskId))
        .range([0, this.width])
        .padding(0.3);
      
      // Determine y-scale domain based on metric
      let yMin = 0;
      let yMax;
      
      switch (this.selectedMetric) {
        case 'time':
          yMax = d3.max(data, d => d.avgCompletionTime) * 1.1;
          break;
        case 'success':
          yMax = 100;
          break;
        case 'errors':
          yMax = d3.max(data, d => d.errorRate) * 1.1;
          break;
      }
      
      const y = d3.scaleLinear()
        .domain([yMin, yMax])
        .range([this.height, 0]);
      
      // Update axes
      const xAxis = this.chart.select('.x-axis')
        .transition()
        .duration(500)
        .call(d3.axisBottom(x)
          .tickFormat(taskId => {
            const task = data.find(d => d.taskId === taskId);
            // Return shortened task name if too long
            return task ? (task.taskName.length > 15 ? task.taskName.substring(0, 12) + '...' : task.taskName) : '';
          }));
      
      // Rotate x-axis labels
      xAxis.selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-.8em')
        .attr('dy', '.15em')
        .attr('transform', 'rotate(-45)');
      
      this.chart.select('.y-axis')
        .transition()
        .duration(500)
        .call(d3.axisLeft(y));
      
      // Update y-axis label
      this.chart.select('.y-label')
        .text(this.metricLabel);
      
      // Remove existing bars
      this.chart.selectAll('.bar').remove();
      
      // Add bars
      const bars = this.chart.selectAll('.bar')
        .data(data)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.taskId))
        .attr('width', x.bandwidth())
        .attr('y', d => y(this.getMetricValue(d)))
        .attr('height', d => this.height - y(this.getMetricValue(d)))
        .attr('fill', d => {
          // Color based on metric
          switch (this.selectedMetric) {
            case 'time':
              return '#1976D2';  // Blue
            case 'success':
              return '#4CAF50';  // Green
            case 'errors':
              return '#FFC107';  // Amber/yellow
          }
        });
      
      // Add value labels
      this.chart.selectAll('.bar-label')
        .data(data)
        .enter()
        .append('text')
        .attr('class', 'bar-label')
        .attr('x', d => x(d.taskId) + x.bandwidth() / 2)
        .attr('y', d => y(this.getMetricValue(d)) - 5)
        .attr('text-anchor', 'middle')
        .text(d => this.formatValue(this.getMetricValue(d)))
        .style('font-size', '10px');
    },
    
    onResize() {
      if (this.$refs.chartContainer) {
        // Clear and reinitialize on resize
        d3.select(this.$refs.chartContainer).select('svg').remove();
        this.initChart();
      }
    }
  }
};
</script>

<style scoped>
.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.chart-container {
  width: 100%;
  height: 400px;
}
</style>