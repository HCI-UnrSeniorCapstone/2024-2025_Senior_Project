import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import UserStudies from '../views/UserStudies.vue'
import StudyForm from '../views/StudyForm.vue'
import SessionReporting from '../views/SessionReporting.vue'
import DataAnalytics from '../views/DataAnalytics.vue'
import PingServer from '../views/PingServer.vue'
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
          path: '/StudyForm',
          name: 'StudyForm',
          component: StudyForm,
        },
        {
          path: '/SessionReporting',
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
      ],
    },
  ],
})

export default router
