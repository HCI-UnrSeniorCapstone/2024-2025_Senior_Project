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
          <!-- Custom render for p-value with colored indicator -->
          <template v-slot:item.successRate="{ item }">
            <v-chip
              small
              :color="getPValueColor(item.pValue || 0.5)"
              text-color="white"
              class="px-2"
            >
              {{ formatPValue(item.pValue || 0.5) }}
            </v-chip>
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
        { text: 'P-Value', value: 'pValue', width: '20%' }
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
    
    // Format p-value for display
    formatPValue(pValue) {
      // Convert p-value to confidence percentage
      const confidence = (1 - pValue) * 100;
      return confidence.toFixed(1) + '% ' + (pValue < 0.05 ? '★' : '');
    },
    
    // Return color based on p-value significance
    getPValueColor(pValue) {
      if (pValue < 0.01) return 'purple darken-2';  // Very significant
      if (pValue < 0.05) return 'blue darken-1';    // Significant
      if (pValue < 0.1) return 'amber darken-2';    // Marginally significant
      return 'grey';                                // Not significant
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