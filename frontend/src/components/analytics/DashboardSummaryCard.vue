<template>
  <div class="summary-card" :class="cardColorClass">
    <div class="card-header">
      <div class="header-content">
        <div class="icon-container"   :class="iconColorClass">
          <v-icon>{{ getIconForTitle(title) }}</v-icon>
        </div>
        <div class="title-container">
          <h3 class="card-title">{{ title }}</h3>
          <div 
            v-if="change !== null" 
            class="change-badge"
            :class="changeClass"
          >
            <span v-if="change > 0">↑</span>
            <span v-else-if="change < 0">↓</span>
            <span v-else>–</span>
            {{ Math.abs(change).toFixed(1) }}%
          </div>
        </div>
      </div>
    </div>
    
    <div class="card-body">
      <div class="metric-value" :class="valueColorClass">
        {{ formattedValue }}
      </div>
      <div class="metric-description">
        {{ description }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardSummaryCard',
  props: {
    // Card's main title
    title: {
      type: String,
      required: true
    },
    // Primary metric value
    value: {
      type: [Number, String],
      required: true
    },
    // Optional description text
    description: {
      type: String,
      default: ''
    },
    // Formatting type for the value
    format: {
      type: String,
      default: 'number',
      validator: (value) => ['number', 'percent', 'time', 'decimal'].includes(value)
    },
    // Percentage change value
    change: {
      type: Number,
      default: null
    },
    // Determines if positive change is considered good
    positiveIsGood: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    // Determine card color based on title
    cardColorClass() {
      const baseClass = 'elevation-2';
      switch (this.title) {
        case 'Participants':
          return `${baseClass} card-participants`;
        case 'Avg Completion Time':
          return `${baseClass} card-time`;
        case 'Success Rate':
          return `${baseClass} card-success`;
        case 'Avg Error Count':
          return `${baseClass} card-error`;
        default:
          return baseClass;
      }
    },
    // Set icon color based on title
    iconColorClass() {
      switch (this.title) {
        case 'Participants':
          return 'icon-participants';
        case 'Avg Completion Time':
          return 'icon-time';
        case 'Success Rate':
          return 'icon-success';
        case 'Avg Error Count':
          return 'icon-error';
        default:
          return '';
      }
    },
    // Set value color based on title
    valueColorClass() {
      switch (this.title) {
        case 'Participants':
          return 'value-participants';
        case 'Avg Completion Time':
          return 'value-time';
        case 'Success Rate':
          return 'value-success';
        case 'Avg Error Count':
          return 'value-error';
        default:
          return '';
      }
    },
    // Format the value based on specified format
    formattedValue() {
      try {
        // Handle null or undefined values
        if (this.value === null || 
            this.value === undefined || 
            (typeof this.value === 'number' && isNaN(this.value))) {
          return '–';
        }

        // Ensure we're working with a number
        const numValue = Number(this.value);
        
        // Additional check for invalid conversions
        if (isNaN(numValue)) {
          return '–';
        }

        switch (this.format) {
          case 'percent':
            return `${numValue.toFixed(1)}%`;
          case 'time':
            // Convert seconds to time format
            const hours = Math.floor(numValue / 3600);
            const mins = Math.floor((numValue % 3600) / 60);
            const secs = Math.floor(numValue % 60);
            
            if (hours > 0) {
              return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
            }
            return `${mins}:${secs.toString().padStart(2, '0')}`;
          case 'decimal':
            return numValue.toFixed(2);
          case 'number':
          default:
            // Format with commas for readability
            return numValue.toLocaleString();
        }
      } catch (error) {
        console.error(`Error formatting value:`, error);
        return '–';
      }
    },
    // Determine change badge class
    changeClass() {
      if (this.change === null || this.change === 0) return 'change-neutral';
      
      const isPositive = this.change > 0;
      const isGood = (isPositive && this.positiveIsGood) || (!isPositive && !this.positiveIsGood);
      
      return isGood ? 'change-positive' : 'change-negative';
    }
  },
  methods: {
    // Get icon based on title
    getIconForTitle(title) {
      const icons = {
        'Participants': 'mdi-account-group',
        'Avg Completion Time': 'mdi-clock-outline',
        'Success Rate': 'mdi-check-circle-outline',
        'Avg Error Count': 'mdi-alert-circle-outline'
      };
      return icons[title] || 'mdi-chart-box';
    }
  }
};
</script>

<style scoped>
/* Card base styles */
.summary-card {
  border-radius: 8px;
  overflow: hidden;
  background-color: white;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.summary-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

/* Card header styles */
.card-header {
  padding: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  align-items: center;
}

.icon-container {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.title-container {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  color: rgba(0, 0, 0, 0.7);
}

/* Change badge styles */
.change-badge {
  padding: 4px 8px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
}

.change-positive {
  background-color: rgba(76, 175, 80, 0.15);
  color: rgb(76, 175, 80);
}

.change-negative {
  background-color: rgba(244, 67, 54, 0.15);
  color: rgb(244, 67, 54);
}

.change-neutral {
  background-color: rgba(0, 0, 0, 0.05);
  color: rgba(0, 0, 0, 0.5);
}

/* Card body styles */
.card-body {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.metric-description {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.6);
}

/* Card theme colors */
.card-participants {
  border-top: 3px solid #1976D2;
}

.card-time {
  border-top: 3px solid #4CAF50;
}

.card-success {
  border-top: 3px solid #2196F3;
}

.card-error {
  border-top: 3px solid #F44336;
}

/* Icon theme colors */
.icon-participants {
  background-color: rgba(25, 118, 210, 0.15);
  color: #1976D2;
}

.icon-time {
  background-color: rgba(76, 175, 80, 0.15);
  color: #4CAF50;
}

.icon-success {
  background-color: rgba(33, 150, 243, 0.15);
  color: #2196F3;
}

.icon-error {
  background-color: rgba(244, 67, 54, 0.15);
  color: #F44336;
}

/* Value theme colors */
.value-participants {
  color: #1976D2;
}

.value-time {
  color: #4CAF50;
}

.value-success {
  color: #2196F3;
}

.value-error {
  color: #F44336;
}
</style>