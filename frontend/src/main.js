import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './views/Home.vue'
import Products from './views/Products.vue'
import PhlowBooks from './views/PhlowBooks.vue'
import Docs from './views/Docs.vue'
import About from './views/About.vue'
import Login from './views/Login.vue'
import Signup from './views/Signup.vue'
import VerifyEmail from './views/VerifyEmail.vue'
import AppDashboard from './views/AppDashboard.vue'
import ClientNew from './views/ClientNew.vue'
import ClientDetail from './views/ClientDetail.vue'
import ClientReview from './views/ClientReview.vue'
import ClientArchive from './views/ClientArchive.vue'
import ClientReconciliation from './views/ClientReconciliation.vue'
import ClientCompliance from './views/ClientCompliance.vue'
import ClientPortalUpload from './views/ClientPortalUpload.vue'
import ComingSoon from './views/ComingSoon.vue'
import { getToken } from './api'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/products', name: 'products', component: Products },
    { path: '/phlowbooks', name: 'phlowbooks', component: PhlowBooks },
    { path: '/docs', name: 'docs', component: Docs },
    { path: '/about', name: 'about', component: About },
    { path: '/login', name: 'login', component: Login },
    { path: '/signup', name: 'signup', component: Signup },
    { path: '/verify-email', name: 'verify-email', component: VerifyEmail },
    { path: '/app', name: 'app', component: AppDashboard, meta: { requiresAuth: true } },
    { path: '/app/clients/new', name: 'client-new', component: ClientNew, meta: { requiresAuth: true } },
    { path: '/app/clients/:id', name: 'client-detail', component: ClientDetail, meta: { requiresAuth: true } },
    { path: '/app/clients/:id/review', name: 'client-review', component: ClientReview, meta: { requiresAuth: true } },
    { path: '/app/clients/:id/archive', name: 'client-archive', component: ClientArchive, meta: { requiresAuth: true } },
    { path: '/app/clients/:id/reconciliation', name: 'client-reconciliation', component: ClientReconciliation, meta: { requiresAuth: true } },
    { path: '/app/clients/:id/compliance', name: 'client-compliance', component: ClientCompliance, meta: { requiresAuth: true } },
    { path: '/portal/:token', name: 'portal-upload', component: ClientPortalUpload, meta: { publicChrome: true } },
  ],
  scrollBehavior(to) {
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !getToken()) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

createApp(App).use(router).mount('#app')
