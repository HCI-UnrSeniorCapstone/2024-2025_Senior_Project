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
    y: participant.errorRate,
    r: Math.max(5, participant.completionRate * 10), // Size based on completion rate
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
                `Error Rate: ${data.y.toFixed(2)}%`,
                `Completion Rate: ${(data.r / 10).toFixed(2) * 100}%`
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
            text: 'Error Rate (%)'
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
