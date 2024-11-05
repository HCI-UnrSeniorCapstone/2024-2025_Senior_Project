import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import Dashboard from '../views/Dashboard.vue'
import StudyReporting from '../views/StudyReporting.vue'
import StudyForm from '../views/StudyForm.vue'
import SessionReporting from '../views/SessionReporting.vue'
import SessionForm from '../views/SessionForm.vue'
import DataAnalytics from '../views/DataAnalytics.vue'


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
          component: Dashboard
        },
        {
          path: '/StudyReporting',
          name: 'StudyReporting',
          component: StudyReporting
        },
        {
          path: '/StudyForm',
          name: 'StudyForm',
          component: StudyForm
        },
        {
          path: '/SessionReporting',
          name: 'SessionReporting',
          component: SessionReporting
        },
        {
          path: '/SessionForm',
          name: 'SessionForm',
          component: SessionForm
        },
        {
          path: '/DataAnalytics',
          name: 'DataAnalytics',
          component: DataAnalytics
        },
      ]
    }
  ]
})

export default router
