import { defineStore } from 'pinia'

export const useStudyStore = defineStore('study', {
  state: () => ({
    currentStudyID: null, // Used when editing or creating a study
    drawerStudyID: null, // Used to reopen the drawer after navigating away
    sessionID: null, // Used by SessionReporting view
    formResetKey: 0,
  }),

  actions: {
    // STUDY ID MANAGEMENT
    setStudyID(id) {
      this.currentStudyID = id
    },
    clearStudyID() {
      this.currentStudyID = null
    },

    // DRAWER MANAGEMENT
    setDrawerStudyID(id) {
      this.drawerStudyID = id
    },
    clearDrawerStudyID() {
      this.drawerStudyID = null
    },

    // SESSION REPORTING
    setSessionID(id) {
      this.sessionID = id
    },
    clearSessionID() {
      this.sessionID = null
    },
    incrementFormResetKey() {
      this.formResetKey++ // Forces Vue to remount form (used on Study Form editing vs new)
    },
  },
})
