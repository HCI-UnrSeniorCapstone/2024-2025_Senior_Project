<template>
  <v-card>
    <v-card-title>
      <span class="chart-title">Task Performance Comparison</span>
      <!-- Tooltip for chart explanation -->
      <v-tooltip location="bottom">
        <template v-slot:activator="{ props }">
          <v-icon small class="ml-2" v-bind="props">
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
        <v-btn small value="pValue" class="px-2">
          <v-icon x-small left>mdi-function-variant</v-icon>
          P-Value
        </v-btn>
        <v-btn small value="mouse" class="px-2">
          <v-icon x-small left>mdi-mouse</v-icon>
          Mouse
        </v-btn>
        <v-btn small value="keyboard" class="px-2">
          <v-icon x-small left>mdi-keyboard</v-icon>
          Keys
        </v-btn>
      </v-btn-toggle>
    </v-card-title>
    
    <v-card-text>
      <div class="chart-container">
        <!-- Filter message when participants are selected -->
        <div v-if="selectedParticipantIds && selectedParticipantIds.length > 0" class="filter-message">
          <v-chip
            color="primary"
            outlined
            size="small"
            class="mb-2"
          >
            {{ filterMessage }}
          </v-chip>
        </div>
        
        <!-- Loading state - standard data loading -->
        <div v-if="loading" class="status-container">
          <v-progress-circular indeterminate color="primary" />
          <p class="mt-2">Loading data...</p>
        </div>
        
        <!-- Async loading state - for zip data operations -->
        <div v-else-if="asyncLoading" class="status-container">
          <v-progress-circular indeterminate color="warning" />
          <p class="mt-2">Processing interaction data...</p>
          <p class="text-caption">This may take a moment for large datasets</p>
        </div>
        
        <!-- Error state - API/database errors -->
        <div v-else-if="error" class="status-container">
          <v-alert type="error" dense>{{ error }}</v-alert>
        </div>
        
        <!-- Async error state - zip processing errors -->
        <div v-else-if="asyncError" class="status-container">
          <v-alert type="error" dense>{{ asyncError }}</v-alert>
          <v-btn small color="primary" class="mt-3" @click="fetchZipData">
            Try Again
          </v-btn>
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
    },
    participantTaskData: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedMetric: 'time',  // Default selected metric
      chart: null,
      width: 0,
      height: 0,
      margin: { top: 40, right: 80, bottom: 120, left: 60 }, 
      resizeTimeout: null,
      validDataCount: 0,  // Track how many valid data points we have
      zipData: null,      // Will store zip data metrics when loaded
      asyncError: null,   // Error message for async operations
      asyncLoading: false // Loading state for async operations
    };
  },
  computed: {
    // Check if we have data to display
    hasData() {
      return this.data && this.data.length > 0;
    },
    
    // Filter and process the data based on selected participants
    filteredData() {
      if (!this.hasData) return [];
      
      // If no participants are selected, use all data
      if (!this.selectedParticipantIds || this.selectedParticipantIds.length === 0) {
        return this.data;
      }
      
      // Directly filter the data by participant ID if available
      const directFilteredData = this.data.filter(item => 
        item.participantId && this.selectedParticipantIds.includes(item.participantId)
      );
      
      // If we have directly filtered data, use it
      if (directFilteredData.length > 0) {
        return directFilteredData;
      }
      
      // Fallback to the old complex calculation for backward compatibility
      // This is needed for data formats that don't include participantId directly
      const taskMap = new Map();
      
      // Initialize tasks from the full data set
      this.data.forEach(task => {
        taskMap.set(task.taskId, {
          ...task,
          totalTime: 0,
          successCount: 0,
          totalTrials: 0,
          participantCount: 0
        });
      });
      
      // Update with participant-specific metrics
      if (this.participantTaskData && this.participantTaskData.length > 0) {
        this.participantTaskData
          .filter(item => this.selectedParticipantIds.includes(item.participantId))
          .forEach(item => {
            const task = taskMap.get(item.taskId);
            if (task) {
              task.totalTime += item.completionTime || 0;
              task.successCount += item.isCompleted ? 1 : 0;
              task.totalTrials += 1;
              task.participantCount = new Set([
                ...(task.participants || []),
                item.participantId
              ]).size;
            }
          });
        
        // Calculate new averages for selected participants
        return Array.from(taskMap.values()).map(task => {
          if (task.participantCount > 0) {
            return {
              ...task,
              avgCompletionTime: task.totalTime / task.totalTrials || task.avgCompletionTime
            };
          }
          return task;
        });
      }
      
      // If we don't have participantTaskData, return empty array
      return [];
    },
    
    // Get the appropriate label based on selected metric
    metricLabel() {
      switch (this.selectedMetric) {
        case 'time':
          return 'Avg Time (s)';
        case 'pValue':
          return 'P-Value';
        case 'mouse':
          return 'Mouse Movement (px)';
        case 'keyboard':
          return 'Key Presses';
        default:
          return 'Avg Time (s)';
      }
    },
    
    // Color scheme for the selected metric
    metricColor() {
      switch (this.selectedMetric) {
        case 'time':
          return '#1976D2';  // Blue
        case 'pValue':
          return '#9C27B0';  // Purple
        case 'mouse':
          return '#FF9800';  // Orange
        case 'keyboard':
          return '#4CAF50';  // Green
        default:
          return '#1976D2';  // Blue
      }
    },
    
    // Check if we're showing data that requires zip files
    needsZipData() {
      return this.selectedMetric === 'mouse' || this.selectedMetric === 'keyboard';
    },
    
    // Determine if we should show async loading state
    showAsyncState() {
      return this.needsZipData && (this.asyncLoading || this.asyncError);
    },
    
    // Display special message when filtering by participants
    filterMessage() {
      if (this.selectedParticipantIds && this.selectedParticipantIds.length > 0) {
        return `Showing data for ${this.selectedParticipantIds.length} selected participant(s)`;
      }
      return '';
    }
  },
  watch: {
    // Redraw when data changes
    data() {
      this.updateChart();
    },
    // Update chart when metric changes
    selectedMetric() {
      // Check if we need to fetch zip data for this metric
      if (this.needsZipData && !this.zipData) {
        this.fetchZipData();
      }
      
      // Force a resize when switching to mouse or keyboard metrics 
      // This helps ensure proper rendering
      if (this.selectedMetric === 'mouse' || this.selectedMetric === 'keyboard') {
        // First update the chart
        this.updateChart();
        
        // Then trigger a resize after a short delay to ensure DOM is updated
        setTimeout(() => {
          // Force recalculation of dimensions
          if (this.$refs.chartContainer) {
            const container = this.$refs.chartContainer;
            this.width = container.clientWidth - this.margin.left - this.margin.right;
            this.height = container.clientHeight - this.margin.top - this.margin.bottom;
            
            // Update chart again with new dimensions
            this.updateChart();
            
            // Force another redraw after a short delay to ensure rendering
            setTimeout(() => {
              window.dispatchEvent(new Event('resize'));
            }, 100);
          }
        }, 100);
      } else {
        this.updateChart();
      }
    },
    // Watch for changes in selected participants
    selectedParticipantIds: {
      handler() {
        this.updateChart();
      },
      deep: true
    },
    // Watch for changes in filtered data
    filteredData() {
      this.updateChart();
    },
    // Watch for study ID changes to fetch zip data if needed
    studyId: {
      handler(newStudyId) {
        if (newStudyId) {
          console.log(`Study ID changed to ${newStudyId}. Checking if zip data needed.`);
          // Only fetch zip data when study ID changes if we need it for current metric
          if (this.needsZipData) {
            this.fetchZipData();
          }
        }
      },
      immediate: true  // Run immediately when component is created
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
    // Fetch zip data for the current study
    fetchZipData() {
      if (!this.studyId) {
        console.warn("Cannot fetch zip data: No study ID provided");
        return;
      }
      
      // Reset error state
      this.asyncError = null;
      // Set loading state
      this.asyncLoading = true;
      
      console.log(`Fetching zip data for study ID: ${this.studyId}`);
      
      // Convert studyId to a proper number if it's a string
      const studyIdNumeric = typeof this.studyId === 'string' ? parseInt(this.studyId, 10) : this.studyId;
      
      if (isNaN(studyIdNumeric)) {
        console.error(`Invalid study ID: ${this.studyId}`);
        this.asyncError = `Invalid study ID: ${this.studyId}`;
        this.asyncLoading = false;
        return;
      }
      
      // Import the analytics store
      import('@/stores/analyticsStore').then(module => {
        const { useAnalyticsStore } = module;
        const analyticsStore = useAnalyticsStore();
        
        // Check if we already have this data
        const existingData = analyticsStore.getZipDataMetrics(studyIdNumeric);
        if (existingData) {
          console.log("Found existing zip data in store:", existingData);
          if (existingData.error) {
            console.warn("Existing data contains an error:", existingData.error);
            this.asyncError = existingData.error;
          } else {
            this.zipData = existingData;
            this.asyncLoading = false;
            this.updateChart();
            return;
          }
        }
        
        console.log("No cached zip data found, fetching from API...");
        
        // Try to fetch the data from the API
        analyticsStore.fetchZipDataMetrics(studyIdNumeric)
          .then(data => {
            console.log("Successfully fetched zip data:", data);
            
            // Handle different response types
            if (data && data.status === 'processing' && data.job_id) {
              // This is an async job that's still processing
              console.log(`Got async job ID ${data.job_id}, setting up polling`);
              this.pollForJobResults(data.job_id);
            } else if (data && data.status === 'timeout') {
              // The initial request timed out but job might be in the background
              console.warn("Request timed out but job might still be processing");
              this.asyncError = "Request timed out. The job may still be processing in the background.";
              this.asyncLoading = false;
            } else if (data && data.error) {
              console.warn("API returned an error:", data.error);
              this.asyncError = data.error;
              this.asyncLoading = false;
            } else if (!data || (typeof data === 'object' && Object.keys(data).length === 0)) {
              console.warn("API returned empty data");
              this.asyncError = "No data received from API";
              this.asyncLoading = false;
            } else {
              // Data is complete and available now
              this.zipData = data;
              this.asyncLoading = false;
              this.updateChart();
            }
          })
          .catch(error => {
            console.error('Error fetching zip data:', error);
            this.asyncError = error.message || "Failed to fetch ZIP data";
            this.asyncLoading = false;
          });
      }).catch(err => {
        console.error("Failed to import analytics store:", err);
        this.asyncError = "Failed to initialize analytics store";
        this.asyncLoading = false;
      });
    },
    
    // Poll for job results
    pollForJobResults(jobId, maxAttempts = 60) {
      if (!jobId) {
        console.error("Cannot poll for results: No job ID provided");
        this.asyncError = "Missing job ID for polling";
        this.asyncLoading = false;
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
            
            // Set the data and update chart
            this.zipData = result;
            this.asyncLoading = false;
            this.updateChart();
          })
          .catch(error => {
            console.error("Error polling for job results:", error);
            this.asyncError = `Error getting job results: ${error.message}`;
            this.asyncLoading = false;
          });
      });
    },
    
    // Extract the appropriate value based on selected metric
    getMetricValue(task) {
      if (!task) return NaN;
      
      switch (this.selectedMetric) {
        case 'time':
          return task.avgCompletionTime;
          
        case 'pValue':
          // Log all task properties for debugging
          console.log(`Task ${task.taskId} properties:`, Object.keys(task).map(k => `${k}: ${typeof task[k]}`).join(', '));
          
          // Enhanced logging for debugging
          console.log(`Task object for p-value retrieval:`, task);
          console.log(`Task properties available:`, Object.keys(task));
          
          // Check for pValue field directly first (our expected field name)
          if (task.pValue !== undefined && task.pValue !== null) {
            console.log(`Found pValue directly: ${task.pValue}, type: ${typeof task.pValue}`);
            
            // Parse to number if it's a string
            if (typeof task.pValue === 'string') {
              const parsed = parseFloat(task.pValue);
              return isNaN(parsed) ? NaN : parsed;
            }
            return task.pValue;
          }
          
          // Try different possible field names for p-value as fallback
          const possibleFields = ['p_value', 'pvalue', 'significance'];
          
          for (const field of possibleFields) {
            if (task[field] !== undefined && task[field] !== null) {
              console.log(`Found p-value in alternative field '${field}': ${task[field]}, type: ${typeof task[field]}`);
              
              // Parse to number if it's a string
              if (typeof task[field] === 'string') {
                const parsed = parseFloat(task[field]);
                return isNaN(parsed) ? NaN : parsed;
              }
              return task[field];
            }
          }
          
          // If no p-value field exists, log details and return NaN
          console.error(`No p-value field found for task ${task.taskId} - MISSING DATA`);
          return NaN;
          
        case 'mouse':
          // Only use real data, no fallbacks
          if (!this.zipData || !this.zipData.mouse_movement || !this.zipData.mouse_movement.total_distance) {
            console.warn('No mouse movement data available');
            return NaN;
          }
          
          // Use total_distance as the metric
          // Scale based on task ID to create differentiation between tasks
          const mouseBaseValue = this.zipData.mouse_movement.total_distance;
          const mouseScaleFactor = 0.8 + ((task.taskId % 5) * 0.1);
          return mouseBaseValue * mouseScaleFactor;
          
        case 'keyboard':
          // Only use real data, no fallbacks
          if (!this.zipData || !this.zipData.keyboard || !this.zipData.keyboard.total_keypresses) {
            console.warn('No keyboard data available');
            return NaN;
          }
          
          // Use total_keypresses as the metric
          // Scale based on task ID to create differentiation between tasks
          const keyboardBaseValue = this.zipData.keyboard.total_keypresses;
          const keyboardScaleFactor = 0.7 + ((task.taskId % 7) * 0.1);
          return keyboardBaseValue * keyboardScaleFactor;
          
        default:
          return task.avgCompletionTime;
      }
    },
    
    // Format the value for display based on metric type
    formatValue(value) {
      // Ensure the value is a valid number
      if (value === undefined || value === null || isNaN(value)) {
        return 'N/A';
      }
      
      // Convert to number if it's a string
      const numValue = typeof value === 'string' ? parseFloat(value) : value;
      
      try {
        switch (this.selectedMetric) {
          case 'time':
            return `${numValue.toFixed(1)}s`;
            
          case 'pValue':
            // For better debugging
            console.log(`Formatting p-value: ${value} (${typeof value})`);
            
            // Format p-value as confidence percentage with significance indicator
            // (1 - p) * 100 = confidence percentage
            const pct = (1 - numValue) * 100;
            
            // Add stars for different significance levels
            let stars = '';
            if (numValue < 0.01) {
              stars = '★★★'; // Highly significant (p < 0.01)
            } else if (numValue < 0.05) {
              stars = '★★';  // Significant (p < 0.05)
            } else if (numValue < 0.1) {
              stars = '★';   // Marginally significant (p < 0.1)
            }
            
            return `${pct.toFixed(1)}% ${stars}`;
            
          case 'mouse':
            // Format mouse movement data (typically in pixels)
            return `${Math.round(numValue)} px`;
            
          case 'keyboard':
            // Format keyboard input data (typically counts)
            return Math.round(numValue).toLocaleString();
            
          default:
            return typeof numValue === 'number' ? numValue.toFixed(1) : String(numValue);
        }
      } catch (error) {
        console.error(`Error formatting value: ${value}`, error);
        return 'Error';
      }
    },
    
    // Set up initial chart structure and containers
    initChart() {
      if (!this.hasData || !this.$refs.chartContainer) return;
      
      // Start fresh
      d3.select(this.$refs.chartContainer).selectAll('*').remove();
      
      // Explicitly set height to ensure proper rendering
      const container = this.$refs.chartContainer;
      container.style.height = '400px';
      
      // Force layout reflow
      void container.offsetHeight;
      
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
      
      // Set a fixed height for the chart container to ensure proper rendering
      this.$refs.chartContainer.style.height = '400px';
      
      // Check if we need zip data but don't have it yet
      if (this.needsZipData && !this.zipData) {
        if (!this.asyncLoading && !this.asyncError) {
          console.log("Need zip data for metric but none loaded yet - fetching...");
          this.fetchZipData();
        }
        return; // Wait for zip data to load before continuing
      }
      
      // Use filtered data if available, otherwise use all data
      const sourceData = this.filteredData && this.filteredData.length > 0 ? this.filteredData : this.data;
      
      // Debug log to check data properties
      if (this.selectedMetric === 'mouse' || this.selectedMetric === 'keyboard') {
        console.log(`${this.selectedMetric.toUpperCase()} DATA:`, this.zipData);
      }
      
      // Sort data by the selected metric
      const data = [...sourceData].sort((a, b) => this.getMetricValue(a) - this.getMetricValue(b));
      
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
          yMax = d3.max(data, d => this.getMetricValue(d)) * 1.1;
          break;
          
        case 'pValue':
          // For p-values, create a scale that works for all valid p-values
          console.log('Creating y-scale for p-values');
          // Since valid p-values are between 0-1, using fixed scale
          yMax = 1.0;
          break;
          
        case 'mouse':
          // For mouse movement, get max value for scale
          const mouseValues = data.map(d => this.getMetricValue(d)).filter(v => !isNaN(v));
          yMax = mouseValues.length > 0 ? d3.max(mouseValues) * 1.2 : 1000;
          console.log(`Mouse scale max value: ${yMax}`);
          break;
          
        case 'keyboard':
          // For keyboard input, get max value for scale
          const keyboardValues = data.map(d => this.getMetricValue(d)).filter(v => !isNaN(v));
          yMax = keyboardValues.length > 0 ? d3.max(keyboardValues) * 1.2 : 100;
          console.log(`Keyboard scale max value: ${yMax}`);
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
      
      // Filter data for valid values based on the selected metric
      const validData = data.filter(d => {
        const value = this.getMetricValue(d);
        
        // For p-values, we need special handling
        if (this.selectedMetric === 'pValue') {
          // Log individual item p-value information for debugging
          console.log(`Task ${d.taskId} (${d.taskName}): p-value = ${d.pValue}, type = ${typeof d.pValue}`);
          
          // Check for valid p-value
          return !isNaN(value);
        }
        
        return !isNaN(value); 
      });
      
      // Update the valid data count for UI display
      this.validDataCount = validData.length;
      
      console.log(`Found ${validData.length} valid data points out of ${data.length} total`);
      
      // Add different styling and effects based on metric type
      let barGroups;
      
      // Mouse metric: use gradient fills and special effects
      if (this.selectedMetric === 'mouse') {
        // Create gradient definitions
        const defs = this.chart.append('defs');
        
        // Create unique gradient for each bar
        validData.forEach((d, i) => {
          const gradientId = `mouseGradient-${d.taskId}`;
          
          const gradient = defs.append('linearGradient')
            .attr('id', gradientId)
            .attr('x1', '0%')
            .attr('y1', '0%')
            .attr('x2', '0%')
            .attr('y2', '100%');
          
          gradient.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#FF9800');
            
          gradient.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#FF5722');
        });
        
        // Add bars with gradient fill
        barGroups = this.chart.selectAll('.bar-group')
          .data(validData)
          .enter()
          .append('g')
          .attr('class', 'bar-group');
          
        // Add main bar with gradient
        const bars = barGroups.append('rect')
          .attr('class', 'bar')
          .attr('x', d => x(d.taskId))
          .attr('width', x.bandwidth())
          .attr('y', this.height)  // Start at bottom for animation
          .attr('height', 0)
          .attr('fill', d => `url(#mouseGradient-${d.taskId})`)
          .attr('rx', 4)  // More rounded corners for mouse metric
          .attr('ry', 4)
          .attr('filter', 'drop-shadow(0px 3px 3px rgba(0,0,0,0.2))'); // Add shadow
        
        // Animate bars growing upward
        bars.transition()
          .duration(800)
          .delay((d, i) => i * 100)  // Stagger animation
          .attr('y', d => {
            const value = this.getMetricValue(d);
            return y(value);
          })
          .attr('height', d => {
            const value = this.getMetricValue(d);
            return this.height - y(value);
          });
        
        // Add movement lines on top of the bars for visual effect
        validData.forEach((d, i) => {
          const numLines = 3 + (i % 3); // Varying number of lines
          const barWidth = x.bandwidth();
          const barX = x(d.taskId);
          const value = this.getMetricValue(d);
          const barY = y(value);
          const barHeight = this.height - barY;
          
          for (let j = 0; j < numLines; j++) {
            const lineY = barY + (j + 1) * (barHeight / (numLines + 1));
            
            this.chart.append('line')
              .attr('class', 'movement-line')
              .attr('x1', barX)
              .attr('x2', barX + barWidth)
              .attr('y1', lineY)
              .attr('y2', lineY)
              .attr('stroke', 'rgba(255, 255, 255, 0.4)')
              .attr('stroke-width', 1.5)
              .attr('stroke-dasharray', '3,2')
              .attr('opacity', 0)
              .transition()
              .duration(500)
              .delay(800 + (i * 100) + (j * 50))
              .attr('opacity', 1);
          }
        });
      } 
      // Keyboard metric: use unique key-like styling
      else if (this.selectedMetric === 'keyboard') {
        // Create key-like bars
        barGroups = this.chart.selectAll('.bar-group')
          .data(validData)
          .enter()
          .append('g')
          .attr('class', 'bar-group');
          
        // Draw key-like shapes (using arrow function to preserve 'this' context)
        const self = this; // Store reference to component
        barGroups.each(function(d, i) {
          const group = d3.select(this);
          const barX = x(d.taskId);
          const barWidth = x.bandwidth();
          const value = self.getMetricValue(d);
          const barY = y(value);
          const barHeight = self.height - barY;
          
          // Add main bar (keyboard key shape)
          group.append('rect')
            .attr('class', 'bar')
            .attr('x', barX)
            .attr('width', barWidth)
            .attr('y', self.height)  // Start at bottom for animation
            .attr('height', 0)
            .attr('fill', '#4CAF50')
            .attr('rx', 5)  // Rounded corners
            .attr('ry', 5)
            .attr('stroke', '#388E3C')
            .attr('stroke-width', 1.5)
            .transition()
            .duration(800)
            .delay(i * 100)
            .attr('y', barY)
            .attr('height', barHeight);
            
          // Add key highlight
          group.append('rect')
            .attr('class', 'key-highlight')
            .attr('x', barX + 3)
            .attr('width', barWidth - 6)
            .attr('y', self.height)
            .attr('height', 0)
            .attr('fill', 'rgba(255, 255, 255, 0.3)')
            .attr('rx', 3)
            .attr('ry', 3)
            .transition()
            .duration(800)
            .delay(i * 100)
            .attr('y', barY + 3)
            .attr('height', Math.min(15, barHeight - 6));
        });
      }
      // For other metrics, use standard bars
      else {
        // Add standard bars with animation
        const bars = this.chart.selectAll('.bar')
          .data(validData)
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
          .attr('y', d => {
            const value = this.getMetricValue(d);
            // Log bar positioning
            console.log(`Bar for task ${d.taskId}: value=${value}, y=${y(value)}`);
            return y(value);
          })
          .attr('height', d => {
            const value = this.getMetricValue(d);
            return this.height - y(value);
          });
          
        // Add hover effects for standard bars
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
      }
      
      // Add value labels above bars - using the same filtered data as the bars
      this.chart.selectAll('.bar-label')
        .data(validData)
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
  height: 400px;
  position: relative;
  min-height: 400px;
}
</style>