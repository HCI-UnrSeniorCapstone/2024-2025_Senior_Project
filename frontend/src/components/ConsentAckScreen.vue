<template>
  <v-dialog v-model="visible" persistent class="consent-dialog">
    <template v-slot:default="{ isActive }">
      <v-card title="Participant Consent Agreement">
        <v-card-text>
          <pdf-app
            v-if="fileURL"
            :pdf="fileURL"
            style="height: 500px"
            :show-toolbar="true"
            :toolbar-options="{
              zoom: true,
              download: false,
              print: false,
              pager: true,
            }"
          >
          </pdf-app>
          <v-alert v-else type="error" variant="tonal"
            >Error loading consent form</v-alert
          >
        </v-card-text>
        <v-card-actions class="d-flex justify-space-between">
          <v-checkbox
            v-model="acknowledgeVal"
            label="I acknowledge"
          ></v-checkbox>
          <v-btn
            text="Continue"
            :disabled="!acknowledgeVal"
            @click="onAcknowledge"
          ></v-btn>
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
</template>
<script>
import PdfApp from 'vue3-pdf-app'

export default {
  name: 'ConsentAckScreen',
  components: {
    PdfApp,
  },
  props: {
    display: Boolean,
    form: {
      type: [File, null],
      required: true,
      default: null,
    },
    // Only need the fields below for live sessions (not when displaying preview versions)
    participantSessId: {
      type: Number,
      required: false,
    },
    studyId: {
      type: Number,
      required: false,
    },
    liveSession: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      acknowledgeVal: false,
      fileURL: null,
    }
  },
  computed: {
    // Needed to avoid prop mutation
    visible: {
      get() {
        return this.display
      },
      set(newVal) {
        this.$emit('update:display', newVal)
      },
    },
  },
  watch: {
    display(newVal) {
      // Have to create temp URL for local File obj
      if (newVal && this.form instanceof File) {
        this.fileURL = URL.createObjectURL(this.form)
      }
      // Cleanup blob if needed
      else if (!newVal && this.fileURL) {
        URL.revokeObjectURL(this.fileURL)
      }
    },
  },
  methods: {
    onAcknowledge() {
      this.$emit('submit')
      this.$emit('update:display', false)
    },
  },
}
</script>
<style scoped>
.consent-dialog {
  width: 60vw;
  max-width: 1500px;
  max-height: none;
}
</style>
