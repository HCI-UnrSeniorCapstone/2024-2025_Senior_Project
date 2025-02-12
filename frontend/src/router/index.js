import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import UserStudies from '../views/UserStudies.vue'
import StudyForm from '../views/StudyForm.vue'
import SessionReporting from '../views/SessionReporting.vue'
import DataAnalytics from '../views/DataAnalytics.vue'
import PingServer from '../views/PingServer.vue'
import TestDB from '../views/TestDB.vue'
import SessionForm from '../views/SessionForm.vue'
import TestSendCSV from '../views/TestCSVToServer.vue'
import TestGetCSVInfo from '../views/TestGetCSVInfo.vue'
import TestGetParticipantSessionCSVInfo from '../views/TestGetParticipantSessionCSVInfo.vue'
import axios from 'axios'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  linkExactActiveClass: 'v-item-active',
  routes: [
    {
      path: '/',
      redirect: '/Dashboard',
      component: MainLayout,
      children: [
        {
          path: '/Dashboard',
          name: 'Dashboard',
          component: Dashboard,
        },
        {
          path: '/UserStudies',
          name: 'UserStudies',
          component: UserStudies,
        },
        {
          // Id not required (only needed when editing study)
          path: '/StudyForm/:studyID?/:userID?',
          name: 'StudyForm',
          component: StudyForm,
        },
        {
          path: '/SessionReporting/:id',
          name: 'SessionReporting',
          component: SessionReporting,
        },
        {
          path: '/DataAnalytics',
          name: 'DataAnalytics',
          component: DataAnalytics,
        },
        // TEMP to show pinging server using router
        {
          path: '/PingServer',
          name: 'Ping',
          component: PingServer,
        },
        // TEMP to show reading database using router
        {
          path: '/Test',
          name: 'TestDB',
          component: TestDB,
        },
        {
          path: '/SessionForm/:id',
          name: 'SessionForm',
          component: SessionForm,
        },
        {
          path: '/TestSendCSV',
          name: 'TestSendCSV',
          component: TestSendCSV,
        },
        {
          path: '/TestGetCSVInfo',
          name: 'TestGetCSVInfo',
          component: TestGetCSVInfo,
        },
        {
          path: '/TestGetParticipantSessionCSVInfo',
          name: 'TestGetParticipantSessionCSVInfo',
          component: TestGetParticipantSessionCSVInfo,
        },
      ],
    },
  ],
})

export default router
