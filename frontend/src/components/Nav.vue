<template>
  <nav :class="{ 'app-nav': isAppRoute }">
    <div class="container nav-inner">
      <router-link :to="isAppRoute ? '/app' : '/'" class="brand">
        <span class="logo">P</span>
        <span>Phlow</span>
      </router-link>
      <div v-if="isAppRoute" class="links app-links">
        <router-link to="/app/clients/new" class="primary-link">New client</router-link>
        <button type="button" @click="logout">Log out</button>
      </div>
      <div v-else class="links">
        <router-link to="/products">Platform</router-link>
        <router-link to="/docs">Docs</router-link>
        <router-link to="/about">About</router-link>
        <router-link to="/login">Log in</router-link>
        <router-link to="/signup" class="signup-link">Sign up</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearToken } from '../api'

const route = useRoute()
const router = useRouter()
const isAppRoute = computed(() => route.path.startsWith('/app'))

function logout() {
  clearToken()
  router.push('/login')
}
</script>

<style scoped>
nav {
  border-bottom: 1px solid var(--border);
  padding: 16px 0;
  background: var(--surface);
  position: sticky;
  top: 0;
  z-index: 10;
}
nav.app-nav {
  padding: 12px 0;
}
nav.app-nav .nav-inner {
  max-width: var(--app-max-width);
}
.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  font-size: 1.05em;
  color: var(--text);
}
.logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: var(--accent);
  color: white;
  font-size: 0.9em;
  font-weight: 700;
}
.links {
  display: flex;
  align-items: center;
  gap: 24px;
}
.links a {
  color: var(--muted);
  font-size: 0.95em;
}
.links a:hover,
.links a.router-link-active {
  color: var(--text);
}
.signup-link {
  color: var(--text) !important;
}
.app-links {
  gap: 14px;
}
.app-links button,
.primary-link {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface-2);
  color: var(--text);
  cursor: pointer;
  font: inherit;
  padding: 8px 14px;
}
.primary-link {
  background: var(--accent);
  border-color: var(--accent);
  color: white !important;
  font-weight: 600;
}
.primary-link:hover {
  background: var(--accent-hover);
  border-color: var(--accent-hover);
  color: white !important;
}
.app-links button:hover {
  background: var(--surface);
  color: var(--text);
  border-color: var(--accent);
}

@media (max-width: 720px) {
  .nav-inner {
    align-items: flex-start;
    flex-direction: column;
    gap: 14px;
  }
  .links {
    flex-wrap: wrap;
    gap: 14px 18px;
  }
}
</style>
