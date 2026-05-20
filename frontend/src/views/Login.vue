<template>
  <div class="auth-page">
    <section class="auth-panel">
      <p class="eyebrow">Phlow</p>
      <h1>Log in</h1>
      <form @submit.prevent="onSubmit">
        <label>
          Email
          <input v-model="email" type="email" autocomplete="email" required />
        </label>
        <label>
          Password
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="resendMessage" class="success">{{ resendMessage }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Log in' }}
        </button>
        <button
          v-if="needsVerification"
          type="button"
          class="resend"
          :disabled="resending"
          @click="resendVerification"
        >
          {{ resending ? 'Sending...' : 'Resend verification email' }}
        </button>
      </form>
      <p class="switch">
        New to Phlow?
        <router-link to="/signup">Create an account</router-link>
      </p>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch, setToken } from '../api'

const router = useRouter()
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const needsVerification = ref(false)
const resending = ref(false)
const resendMessage = ref('')

async function onSubmit() {
  loading.value = true
  error.value = ''
  resendMessage.value = ''
  needsVerification.value = false

  try {
    const data = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: email.value, password: password.value }),
    })
    setToken(data.access_token)
    router.push('/app')
  } catch (err) {
    error.value = err.message
    if (/verify/i.test(err.message)) {
      needsVerification.value = true
    }
  } finally {
    loading.value = false
  }
}

async function resendVerification() {
  resending.value = true
  resendMessage.value = ''
  try {
    const data = await apiFetch('/auth/resend-verification', {
      method: 'POST',
      body: JSON.stringify({ email: email.value }),
    })
    resendMessage.value = data?.message || 'A new verification email is on its way.'
  } catch (err) {
    error.value = err.message
  } finally {
    resending.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 520px;
  display: grid;
  place-items: center;
  padding: 24px;
}
.auth-panel {
  width: min(100%, 420px);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 32px;
}
.eyebrow {
  color: var(--accent-hover);
  font-size: 0.8em;
  font-weight: 700;
  margin-bottom: 8px;
  text-transform: uppercase;
}
h1 {
  margin-bottom: 24px;
}
form {
  display: grid;
  gap: 16px;
}
label {
  display: grid;
  gap: 6px;
  color: var(--muted);
  font-size: 0.92em;
}
input {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--bg);
  color: var(--text);
  padding: 12px 14px;
  font: inherit;
}
input:focus {
  outline: none;
  border-color: var(--accent);
}
button {
  border: 0;
  border-radius: 8px;
  background: var(--accent);
  color: white;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
  padding: 12px 16px;
}
button:disabled {
  cursor: wait;
  opacity: 0.7;
}
.error {
  color: #fca5a5;
  font-size: 0.92em;
}
.success {
  color: #86efac;
  font-size: 0.92em;
}
button.resend {
  background: var(--surface-2);
  color: var(--text);
  border: 1px solid var(--border);
}
.switch {
  color: var(--muted);
  margin-top: 20px;
  font-size: 0.92em;
}
</style>
