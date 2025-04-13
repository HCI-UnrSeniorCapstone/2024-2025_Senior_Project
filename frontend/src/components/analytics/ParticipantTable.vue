<template>
  <v-card>
    <v-card-title>
      Participant Data
      <v-spacer></v-spacer>
      <!-- Search field to filter the table -->
      <v-text-field
        v-model="search"
        append-icon="mdi-magnify"
        label="Search"
        single-line
        hide-details
        dense
        outlined
        class="search-field"
      ></v-text-field>
    </v-card-title>
    <v-card-text>
      <!-- Loading state -->
      <div v-if="loading" class="loading-container">
        <v-progress-circular indeterminate color="primary" />
        <p class="mt-2">Loading participant data...</p>
      </div>
      
      <!-- Error state -->
      <div v-else-if="error" class="error-container">
        <v-alert type="error" dense>{{ error }}</v-alert>
      </div>
      
      <!-- Empty state -->
      <div v-else-if="!hasData" class="empty-container">
        <v-icon size="48" color="grey lighten-1">mdi-account-group-outline</v-icon>
        <p class="mt-2">No participant data available</p>
      </div>
      
      <!-- Data table display -->
      <div v-else>
        <v-data-table
          :headers="headers"
          :items="participants"
          :search="search"
          :items-per-page="10"
          :footer-props="{
            'items-per-page-options': [5, 10, 15, 20, -1],
            'items-per-page-text': 'Participants per page'
          }"
          :loading="loading"
          class="participant-table"
        >
          <!-- Custom render for success rate with colored progress bar -->
          <template v-slot:item.successRate="{ item }">
            <v-progress-linear
              :value="item.successRate"
              height="20"
              :color="getSuccessRateColor(item.successRate)"
              class="rounded-lg"
            >
              <span class="text-caption white--text">{{ item.successRate }}%</span>
            </v-progress-linear>
          </template>
          
          <!-- Format time values as minutes:seconds or hours:minutes:seconds -->
          <template v-slot:item.completionTime="{ item }">
            {{ formatTime(item.completionTime) }}
          </template>
        </v-data-table>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'ParticipantTable',
  props: {
    participants: {
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
      search: '',  // Search query for filtering
      headers: [
        { text: 'ID', value: 'participantId', width: '15%' },
        { text: 'Sessions', value: 'sessionCount', width: '15%' },
        { text: 'Time', value: 'completionTime', width: '20%' },
        { text: 'Success Rate', value: 'successRate', width: '30%' },
        { text: 'Errors', value: 'errorCount', width: '20%' }
      ]
    };
  },
  computed: {
    // Quick check if we have data to display
    hasData() {
      return this.participants && this.participants.length > 0;
    }
  },
  methods: {
    // Convert seconds to readable time format
    formatTime(seconds) {
      if (!seconds) return 'N/A';
      
      // Format as minutes and seconds if less than an hour
      if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.round(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
      }
      
      // Format as hours, minutes, and seconds
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const remainingSeconds = Math.round(seconds % 60);
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    },
    
    // Return color based on success rate percentage
    getSuccessRateColor(rate) {
      if (rate >= 80) return 'success';  // Green for high success
      if (rate >= 60) return 'info';     // Blue for good success
      if (rate >= 40) return 'warning';  // Orange for moderate success
      return 'error';                    // Red for low success
    }
  }
};
</script>

<style scoped>
.search-field {
  max-width: 300px;
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.participant-table {
  width: 100%;
}
</style>