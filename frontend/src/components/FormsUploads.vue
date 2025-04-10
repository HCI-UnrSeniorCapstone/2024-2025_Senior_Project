<template>
  <v-container fluid>
    <FileUploadAndPreview
      :modelValue="consentForm"
      @update:modelValue="$emit('update:consentForm', $event)"
      label="Consent Form (PDF)"
      accept=".pdf,.txt,.md"
      @preview="previewConsentForm"
    />

    <FileUploadAndPreview
      :modelValue="preSurveyFile"
      @update:modelValue="$emit('update:preSurveyFile', $event)"
      label="Pre-survey Questionnaire (YAML)"
      accept=".yaml,.yml"
      @preview="previewConsentForm"
    />

    <FileUploadAndPreview
      :modelValue="postSurveyFile"
      @update:modelValue="$emit('update:postSurveyFile', $event)"
      label="Post-survey Questionnaire (YAML)"
      accept=".yaml,.yml"
      @preview="previewConsentForm"
    />

    <ConsentAckScreen
      :display="showConsentPreview"
      @update:display="$emit('update:showConsentPreview', $event)"
      :form="consentForm"
    />
  </v-container>
</template>

<script>
import FileUploadAndPreview from '@/components/FileUploadAndPreview.vue'
import ConsentAckScreen from '@/components/ConsentAckScreen.vue'

export default {
  components: {
    FileUploadAndPreview,
    ConsentAckScreen,
  },
  props: {
    consentForm: File,
    preSurveyFile: File,
    postSurveyFile: File,
    showConsentPreview: Boolean,
  },
  emits: [
    'update:consentForm',
    'update:preSurveyFile',
    'update:postSurveyFile',
    'update:showConsentPreview',
  ],
  methods: {
    previewConsentForm() {
      if (this.consentForm) {
        this.$emit('update:showConsentPreview', true)
      }
    },
  },
}
</script>
