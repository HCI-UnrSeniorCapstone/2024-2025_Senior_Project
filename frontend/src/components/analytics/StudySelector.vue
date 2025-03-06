<template>
  <div class="study-selector">
    <!-- Main study dropdown with search -->
    <v-select
      :value="value"
      :items="studyOptions"
      item-text="name"
      item-value="id"
      label="Select Study"
      outlined
      dense
      :loading="loading"
      :error-messages="errorMessage"
      :disabled="disabled || loading || studies.length === 0"
      @input="$emit('input', $event)"
      @change="$emit('change', $event)"
    >
      <!-- Study icon -->
      <template v-slot:prepend-inner>
        <v-icon small color="primary">mdi-clipboard-text</v-icon>
      </template>
      
      <!-- Custom display for selected study -->
      <template v-slot:selection="{ item }">
        <div class="study-selection">
          <span class="study-name">{{ item.name }}</span>
          <span v-if="item.stats" class="study-stats">
            {{ item.stats.participants }} participants
          </span>
        </div>
      </template>
      
      <!-- Empty state when no studies exist -->
      <template v-slot:no-data>
        <div class="pa-2 text-center">
          <v-icon color="grey lighten-1" size="24">mdi-alert-circle-outline</v-icon>
          <p class="mb-0 mt-1">No studies available</p>
        </div>
      </template>
    </v-select>
    
    <!-- Refresh button with tooltip -->
    <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <div class="d-inline-block ml-2">
          <v-btn
            icon
            small
            color="primary"
            @click="refreshStudies"
            :loading="loading"
            :disabled="disabled"
            v-bind="attrs"
            v-on="on"
          >
            <v-icon small>mdi-refresh</v-icon>
          </v-btn>
        </div>
      </template>
      <span>Refresh study list</span>
    </v-tooltip>
  </div>
</template>

<script>
export default {
  name: 'StudySelector',
  props: {
    // Selected study ID (for v-model binding)
    value: {
      type: [String, Number],
      default: null
    },
    
    // List of studies to display in dropdown
    studies: {
      type: Array,
      default: () => []
    },
    
    // Show loading spinner when fetching studies
    loading: {
      type: Boolean,
      default: false
    },
    
    // Display error message under the select
    errorMessage: {
      type: String,
      default: ''
    },
    
    // Disable interaction with the component
    disabled: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    // Process studies data for the dropdown
    studyOptions() {
      return this.studies.map(study => ({
        id: study.id,
        name: study.name,
        description: study.description,
        status: study.status || 'Active',
        stats: study.stats || null
      }));
    }
  },
  methods: {
    // Trigger parent component to refresh studies
    refreshStudies() {
      this.$emit('refresh');
    }
  }
};
</script>

<style scoped>
.study-selector {
  display: flex;
  align-items: center;
  min-width: 250px;
}

.study-selection {
  display: flex;
  flex-direction: column;
}

.study-name {
  font-weight: 500;
}

.study-stats {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.6);
}
</style>