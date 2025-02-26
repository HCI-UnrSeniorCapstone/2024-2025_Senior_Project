<template>
  <v-card>
    <v-card-title>
      <span>Learning Curve</span>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-icon small class="ml-2" v-bind="attrs" v-on="on">
            mdi-information-outline
          </v-icon>
        </template>
        <span>Shows how task completion time changes across attempts</span>
      </v-tooltip>
      <v-spacer></v-spacer>
      <v-btn-toggle v-model="selectedView" mandatory>
        <v-btn small value="all">All Tasks</v-btn>
        <v-btn small value="individual">By Task</v-btn>
      </v-btn-toggle>
    </v-card-title>
    <v-card-text>
      <div class="chart-container">
        <div v-if="loading" class="loading-state">
          <v-progress-circular indeterminate color="primary" />
          <p class="mt-2">Loading data...</p>
        </div>
        <div v-else-if="error" class="error-state">
          <v-alert type="error" dense>{{ error }}</v-alert>
        </div>
        <div v-else-if="!hasData" class="empty-state">
          <p>No learning curve data available</p>
        </div>
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
    }
  },
  data() {
    return {
      selectedView: 'all',
      chart: null,
      width: 0,
      height: 0,
      margin: { top: 20, right: 80, bottom: 50, left: 60 }
    };
  },
  computed: {
    hasData() {
      return this.data && this.data.length > 0;
    },
    processedData() {
      if (!this.hasData) return [];
      
      if (this.selectedView === 'all') {
        // Average across all tasks
        const attemptMap = new Map();
        
        this.data.forEach(item => {
          if (!attemptMap.has(item.attempt)) {
            attemptMap.set(item.attempt, {
              attempt: item.attempt,
              times: [],
              errors: []
            });
          }
          
          const entry = attemptMap.get(item.attempt);
          entry.times.push(item.completionTime);
          entry.errors.push(item.errorCount);
        });
        
        return Array.from(attemptMap.values()).map(entry => ({
          attempt: entry.attempt,
          completionTime: d3.mean(entry.times),
          errorCount: d3.mean(entry.errors)
        })).sort((a, b) => a.attempt - b.attempt);
      } else {
        // Group by task
        const taskMap = new Map();
        
        this.data.forEach(item => {
          if (!taskMap.has(item.taskId)) {
            taskMap.set(item.taskId, []);
          }
          
          taskMap.get(item.taskId).push(item);
        });
        
        const result = [];
        
        taskMap.forEach((items, taskId) => {
          const taskData = items.sort((a, b) => a.attempt - b.attempt);
          result.push({
            taskId,
            taskName: taskData[0].taskName,
            data: taskData
          });
        });
        
        return result;
      }
    }
  },
  watch: {
    processedData() {
      this.updateChart();
    },
    selectedView() {
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
      
      // Add axis labels
      this.chart.append('text')
        .attr('class', 'x-label')
        .attr('text-anchor', 'middle')
        .attr('x', this.width / 2)
        .attr('y', this.height + 40)
        .text('Attempt Number');
      
      this.chart.append('text')
        .attr('class', 'y-label')
        .attr('text-anchor', 'middle')
        .attr('transform', `translate(${-this.margin.left + 15},${this.height / 2}) rotate(-90)`)
        .text('Completion Time (s)');
      
      // Add legend group
      this.chart.append('g')
        .attr('class', 'legend')
        .attr('transform', `translate(${this.width + 10}, 0)`);
      
      this.updateChart();
    },
    
    updateChart() {
      if (!this.chart || !this.hasData) return;
      
      if (this.selectedView === 'all') {
        this.renderAllTasksView();
      } else {
        this.renderIndividualTasksView();
      }
    },
    
    renderAllTasksView() {
      const data = this.processedData;
      
      // Scales
      const x = d3.scaleLinear()
        .domain([1, d3.max(data, d => d.attempt)])
        .range([0, this.width]);
      
      const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.completionTime) * 1.1])
        .range([this.height, 0]);
      
      // Line generator
      const line = d3.line()
        .x(d => x(d.attempt))
        .y(d => y(d.completionTime))
        .curve(d3.curveMonotoneX);
      
      // Update axes
      this.chart.select('.x-axis')
        .transition()
        .duration(500)
        .call(d3.axisBottom(x).ticks(Math.min(data.length, 10)).tickFormat(d3.format('d')));
      
      this.chart.select('.y-axis')
        .transition()
        .duration(500)
        .call(d3.axisLeft(y));
      
      // Remove any existing paths
      this.chart.selectAll('.line-path').remove();
      this.chart.selectAll('.data-point').remove();
      
      // Add the line
      this.chart.append('path')
        .datum(data)
        .attr('class', 'line-path')
        .attr('fill', 'none')
        .attr('stroke', '#1976D2')
        .attr('stroke-width', 2)
        .attr('d', line);
      
      // Add data points
      this.chart.selectAll('.data-point')
        .data(data)
        .enter()
        .append('circle')
        .attr('class', 'data-point')
        .attr('cx', d => x(d.attempt))
        .attr('cy', d => y(d.completionTime))
        .attr('r', 5)
        .attr('fill', '#1976D2');
      
      // Clear legend
      this.chart.select('.legend').selectAll('*').remove();
    },
    
    renderIndividualTasksView() {
      const data = this.processedData;
      
      // Find max values for scales
      const maxAttempt = d3.max(data, d => d3.max(d.data, item => item.attempt));
      const maxTime = d3.max(data, d => d3.max(d.data, item => item.completionTime));
      
      // Scales
      const x = d3.scaleLinear()
        .domain([1, maxAttempt])
        .range([0, this.width]);
      
      const y = d3.scaleLinear()
        .domain([0, maxTime * 1.1])
        .range([this.height, 0]);
      
      const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
      
      // Line generator
      const line = d3.line()
        .x(d => x(d.attempt))
        .y(d => y(d.completionTime))
        .curve(d3.curveMonotoneX);
      
      // Update axes
      this.chart.select('.x-axis')
        .transition()
        .duration(500)
        .call(d3.axisBottom(x).ticks(Math.min(maxAttempt, 10)).tickFormat(d3.format('d')));
      
      this.chart.select('.y-axis')
        .transition()
        .duration(500)
        .call(d3.axisLeft(y));
      
      // Remove any existing paths and points
      this.chart.selectAll('.line-path').remove();
      this.chart.selectAll('.data-point').remove();
      
      // Add lines for each task
      data.forEach((task, i) => {
        const color = colorScale(i);
        
        // Add line
        this.chart.append('path')
          .datum(task.data)
          .attr('class', 'line-path')
          .attr('fill', 'none')
          .attr('stroke', color)
          .attr('stroke-width', 2)
          .attr('d', line);
        
        // Add data points
        this.chart.selectAll(`.data-point-${i}`)
          .data(task.data)
          .enter()
          .append('circle')
          .attr('class', 'data-point')
          .attr('cx', d => x(d.attempt))
          .attr('cy', d => y(d.completionTime))
          .attr('r', 4)
          .attr('fill', color);
      });
      
      // Update legend
      const legend = this.chart.select('.legend');
      legend.selectAll('*').remove();
      
      data.forEach((task, i) => {
        const legendItem = legend.append('g')
          .attr('transform', `translate(0, ${i * 20})`);
        
        legendItem.append('rect')
          .attr('width', 15)
          .attr('height', 15)
          .attr('fill', colorScale(i));
        
        legendItem.append('text')
          .attr('x', 20)
          .attr('y', 12)
          .text(task.taskName);
      });
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
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.chart-content {
  width: 100%;
  height: 400px;
}
</style>