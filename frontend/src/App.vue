<template>
  <router-view v-if="isPublicChrome" />
  <div v-else :class="['layout', { 'review-layout': isReviewRoute }]">
    <Nav />
    <main :class="{ 'review-main': isReviewRoute }">
      <router-view />
    </main>
    <footer v-if="!isReviewRoute">
      <div class="container">
        <p>&copy; 2026 PhlowBooks &middot; Bookkeeping infrastructure for PH firms.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Nav from './components/Nav.vue'

const route = useRoute()
const isReviewRoute = computed(() => route.name === 'client-review')
const isPublicChrome = computed(() => route.meta?.publicChrome === true)
</script>

<style scoped>
.layout {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}
main {
  flex: 1;
  padding: 16px 0 72px;
}
.review-layout {
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
}
main.review-main {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: 12px 0;
}
footer {
  border-top: 1px solid var(--border);
  padding: 24px 0;
  color: var(--muted);
  font-size: 0.9em;
}
</style>
