<template>
  <v-dialog
    v-model="dialog"
    width="800"
    class="participant-details-modal"
  >
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <div class="d-flex align-center">
          <span class="text-h5">Participant {{ participant.participantId }} Details</span>
        </div>
        <v-btn
          icon
          color="purple"
          @click="close"
          class="close-button"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      
      <v-divider></v-divider>
      
      <v-card-text>
        <!-- Key metrics in card format -->
        <v-row class="mt-2">
          <v-col cols="12" md="4">
            <v-card outlined class="metric-card">
              <v-card-text class="d-flex align-center">
                <v-avatar
                  color="purple lighten-4"
                  size="48"
                  class="mr-3"
                >
                  <v-icon color="purple darken-2">mdi-account</v-icon>
                </v-avatar>
                <div>
                  <div class="text-caption text-grey">Participant ID</div>
                  <div class="text-h6">{{ participant.participantId }}</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-card outlined class="metric-card">
              <v-card-text class="d-flex align-center">
                <v-avatar
                  color="purple lighten-4"
                  size="48"
                  class="mr-3"
                >
                  <v-icon color="purple darken-2">mdi-clock-outline</v-icon>
                </v-avatar>
                <div>
                  <div class="text-caption text-grey">Average Completion Time</div>
                  <div class="text-h6">{{ formatTime(participant.completionTime) }}</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-card outlined class="metric-card">
              <v-card-text class="d-flex align-center">
                <v-avatar
                  color="purple lighten-4"
                  size="48"
                  class="mr-3"
                >
                  <v-icon color="purple darken-2">mdi-check-circle-outline</v-icon>
                </v-avatar>
                <div>
                  <div class="text-caption text-grey">Sessions Completed</div>
                  <div class="text-h6">{{ participant.trialCount || 0 }}</div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        
        <!-- Additional information section could be added here in the future -->
        <div class="mt-6 text-center">
          <v-icon color="grey" size="64">mdi-chart-box-outline</v-icon>
          <p class="mt-2 text-grey-darken-1">Participant performance details are available in the analytics dashboard.</p>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'ParticipantDetailsModal',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    participant: {
      type: Object,
      default: () => ({
        participantId: '',
        completionTime: 0,
        trialCount: 0
      })
    }
  },
  data() {
    return {};
  },
  computed: {
    dialog: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit('update:modelValue', value);
      }
    }
  },
  watch: {},
  methods: {
    close() {
      this.dialog = false;
    },
    formatTime(seconds) {
      if (!seconds) return 'N/A';
      
      // Ensure seconds is a number
      const numSeconds = typeof seconds === 'string' ? parseFloat(seconds) : seconds;
      if (isNaN(numSeconds)) return 'N/A';
      
      // Format as seconds if very small
      if (numSeconds < 60) {
        return `${numSeconds.toFixed(1)} sec`;
      }
      
      // Format as minutes and seconds if less than an hour
      if (numSeconds < 3600) {
        const minutes = Math.floor(numSeconds / 60);
        const remainingSeconds = Math.round(numSeconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')} min`;
      }
      
      // Format as hours, minutes, and seconds
      const hours = Math.floor(numSeconds / 3600);
      const minutes = Math.floor((numSeconds % 3600) / 60);
      const remainingSeconds = Math.round(numSeconds % 60);
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')} hrs`;
    },
  }
};
</script>

<style scoped>
.metric-card {
  height: 100%;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.metric-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.task-card {
  height: 100%;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.task-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.close-button {
  position: absolute;
  top: 8px;
  right: 8px;
}
</style>