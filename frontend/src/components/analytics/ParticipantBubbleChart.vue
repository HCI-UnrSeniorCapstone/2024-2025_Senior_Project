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
  
  // Format data for bubble chart, adapting to backend data structure
  const bubbleData = props.participantData.map(participant => {
    // Calculate a size value that ensures bubbles are visible
    const size = participant.completionTime 
      ? Math.max(5, Math.min(30, participant.completionTime / 10)) 
      : 10;
      
    return {
      x: participant.completionTime || 0,  // X-axis: completion time 
      y: 0.5,  // Y-axis: fixed value for simplicity
      r: size, // Size based on completion time, with min/max bounds
      participantId: participant.participantId,
      // Add more data for tooltips - only include what we have
      sessionCount: participant.sessionCount || 1
    };
  });

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
                `P-Value: ${data.y.toFixed(3)}`
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
            text: 'Completion Time (seconds)'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Distribution'
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
