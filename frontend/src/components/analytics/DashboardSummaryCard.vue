<template>
  <div class="summary-card">
    <div class="card-header">
      <h3>{{ title }}</h3>
    </div>
    <div class="card-body">
      <div class="metric-value">{{ formattedValue }}</div>
      <div class="metric-label">{{ description }}</div>
    </div>
    <div v-if="change !== null" class="card-footer">
      <div :class="['change-indicator', changeClass]">
        <span v-if="change > 0">↑</span>
        <span v-else-if="change < 0">↓</span>
        <span v-else>–</span>
        {{ Math.abs(change).toFixed(1) }}%
      </div>
      <div class="period">vs. previous period</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardSummaryCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [Number, String],
      required: true
    },
    description: {
      type: String,
      default: ''
    },
    format: {
      type: String,
      default: 'number' // 'number', 'percent', 'time', 'decimal'
    },
    change: {
      type: Number,
      default: null
    },
    positiveIsGood: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    formattedValue() {
      if (this.value === null || this.value === undefined) {
        return '–';
      }

      switch (this.format) {
        case 'percent':
          return `${Number(this.value).toFixed(1)}%`;
        case 'time':
          // Format seconds as MM:SS
          const mins = Math.floor(Number(this.value) / 60);
          const secs = Math.floor(Number(this.value) % 60);
          return `${mins}:${secs.toString().padStart(2, '0')}`;
        case 'decimal':
          return Number(this.value).toFixed(2);
        case 'number':
        default:
          // Format with commas for thousands
          return Number(this.value).toLocaleString();
      }
    },
    changeClass() {
      if (this.change === null || this.change === 0) return 'neutral';
      
      const isPositive = this.change > 0;
      const isGood = (isPositive && this.positiveIsGood) || (!isPositive && !this.positiveIsGood);
      
      return isGood ? 'positive' : 'negative';
    }
  }
};
</script>

<style scoped>
.summary-card {
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-header h3 {
  color: #4a5568;
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px 0;
}

.card-body {
  flex-grow: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 14px;
  color: #718096;
}

.card-footer {
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.change-indicator {
  font-size: 13px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 16px;
}

.positive {
  color: #38a169;
  background-color: rgba(56, 161, 105, 0.1);
}

.negative {
  color: #e53e3e;
  background-color: rgba(229, 62, 62, 0.1);
}

.neutral {
  color: #718096;
  background-color: rgba(113, 128, 150, 0.1);
}

.period {
  font-size: 12px;
  color: #a0aec0;
}
</style>