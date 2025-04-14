<template>
  <div class="bubble-chart-container">
    <canvas ref="bubbleCanvas" class="bubble-chart"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import Chart from 'chart.js/auto';

const props = defineProps({
  participantData: {
    type: Array,
    required: true
  }
});

const bubbleCanvas = ref(null);
let bubbleChart = null;

function initChart() {
  if (!bubbleCanvas.value || !props.participantData.length) return;
  
  const ctx = bubbleCanvas.value.getContext('2d');
  
  // Format data for bubble chart
  const bubbleData = props.participantData.map(participant => ({
    x: participant.averageCompletionTime,
    y: participant.pValue || 0.05, // Use p-value instead of error rate
    r: Math.max(5, participant.completionTime / 10), // Size based on completion time
    participantId: participant.participantId
  }));

  if (bubbleChart) {
    bubbleChart.destroy();
  }

  bubbleChart = new Chart(ctx, {
    type: 'bubble',
    data: {
      datasets: [{
        label: 'Participants',
        data: bubbleData,
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) => {
              const data = context.raw;
              return [
                `Participant: ${data.participantId}`,
                `Avg. Completion Time: ${data.x.toFixed(1)}s`,
                `P-Value: ${data.y.toFixed(3)}`,
                `Time: ${data.r * 10}s`
              ];
            }
          }
        },
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Average Completion Time (seconds)'
          }
        },
        y: {
          title: {
            display: true,
            text: 'P-Value (significance)'
          }
        }
      }
    }
  });
}

// Initialize and update chart when data changes
onMounted(() => {
  initChart();
});

watch(() => props.participantData, () => {
  initChart();
}, { deep: true });
</script>

<style scoped>
.bubble-chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}

.bubble-chart {
  width: 100%;
  height: 100%;
}
</style>
