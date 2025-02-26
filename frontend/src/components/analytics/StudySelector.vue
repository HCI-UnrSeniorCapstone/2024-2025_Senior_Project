<template>
  <div class="study-selector">
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
      <template v-slot:prepend-inner>
        <v-icon small color="primary">mdi-clipboard-text</v-icon>
      </template>
      <template v-slot:selection="{ item }">
        <div class="study-selection">
          <span class="study-name">{{ item.name }}</span>
          <span v-if="item.stats" class="study-stats">
            {{ item.stats.participants }} participants
          </span>
        </div>
      </template>
      <template v-slot:no-data>
        <div class="pa-2 text-center">
          <v-icon color="grey lighten-1" size="24">mdi-alert-circle-outline</v-icon>
          <p class="mb-0 mt-1">No studies available</p>
        </div>
      </template>
    </v-select>
    
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
    /**
     * Currently selected study ID (v-model)
     */
    value: {
      type: [String, Number],
      default: null
    },
    
    /**
     * List of available studies
     */
    studies: {
      type: Array,
      default: () => []
    },
    
    /**
     * Loading state
     */
    loading: {
      type: Boolean,
      default: false
    },
    
    /**
     * Error message to display
     */
    errorMessage: {
      type: String,
      default: ''
    },
    
    /**
     * Disabled state
     */
    disabled: {
      type: Boolean,
      default: false
    }
  },
  computed: {
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
    /**
     * Refresh study list
     */
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