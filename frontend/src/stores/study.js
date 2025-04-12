import { defineStore } from 'pinia'

export const useStudyStore = defineStore('study', {
  state: () => ({
    currentStudyID: null,
    drawerStudyID: null,
    sessionID: null,
    formResetKey: 0,
  }),

  actions: {
    // Restore from sessionStorage when store is created
    initializeFromSession() {
      const storedStudyID = sessionStorage.getItem('currentStudyID')
      const storedDrawerID = sessionStorage.getItem('drawerStudyID')
      const storedSessionID = sessionStorage.getItem('sessionID')

      if (storedStudyID) this.currentStudyID = Number(storedStudyID)
      if (storedDrawerID) this.drawerStudyID = Number(storedDrawerID)
      if (storedSessionID) this.sessionID = Number(storedSessionID)
    },

    setStudyID(id) {
      this.currentStudyID = id
      sessionStorage.setItem('currentStudyID', id)
    },
    clearStudyID() {
      this.currentStudyID = null
      sessionStorage.removeItem('currentStudyID')
    },

    setDrawerStudyID(id) {
      this.drawerStudyID = id
      sessionStorage.setItem('drawerStudyID', id)
    },
    clearDrawerStudyID() {
      this.drawerStudyID = null
      sessionStorage.removeItem('drawerStudyID')
    },

    setSessionID(id) {
      this.sessionID = id
      sessionStorage.setItem('sessionID', id)
    },
    clearSessionID() {
      this.sessionID = null
      sessionStorage.removeItem('sessionID')
    },

    incrementFormResetKey() {
      this.formResetKey++
    },

    // Optional: nuke everything
    reset() {
      this.clearStudyID()
      this.clearDrawerStudyID()
      this.clearSessionID()
      this.formResetKey = 0
    },
  },
})
