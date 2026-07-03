import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { 
      path: '/', 
      name: 'Login', 
      component: Login 
    },
    { 
      path: '/panel', 
      name: 'Dashboard', 
      component: Dashboard 
    }
  ]
})

export default router