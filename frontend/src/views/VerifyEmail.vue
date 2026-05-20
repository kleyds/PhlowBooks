<template>
  <div class="auth-page">
    <section class="auth-panel">
      <p class="eyebrow">PhlowBooks</p>
      <h1>Verify email</h1>

      <p v-if="status === 'pending'" class="info">Verifying your email...</p>

      <template v-if="status === 'success'">
        <p class="success">Your email is verified! Redirecting you to the app...</p>
      </template>

      <template v-if="status === 'error'">
        <p class="error">{{ message }}</p>
        <p class="info">Need a fresh link? Enter your email below.</p>
        <form @submit.prevent="resend">
          <label>
            Email
            <input v-model="email" type="email" autocomplete="email" required />
          </label>
          <p v-if="resendMessage" class="success">{{ resendMessage }}</p>
          <button type="submit" :disabled="resending">
            {{ resending ? 'Sending...' : 'Send a new link' }}
          </button>
        </form>
        <p class="switch">
          <router-link to="/login">Back to log in</router-link>
        </p>
      </template>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch, setToken } from '../api'

const route = useRoute()
const router = useRouter()
const status = ref('pending')
const message = ref('')
const email = ref('')
const resending = ref(false)
const resendMessage = ref('')

onMounted(async () => {
  const token = (route.query.token || '').toString().trim()
  if (!token) {
    status.value = 'error'
    message.value = 'No verification token in this link.'
    return
  }

  try {
    const data = await apiFetch('/auth/verify-email', {
      method: 'POST',
      body: JSON.stringify({ token }),
    })
    setToken(data.access_token)
    status.value = 'success'
    setTimeout(() => router.push('/app'), 1200)
  } catch (err) {
    status.value = 'error'
    message.value = err.message || 'Verification failed.'
  }
})

async function resend() {
  resending.value = true
  resendMessage.value = ''
  try {
    const data = await apiFetch('/auth/resend-verification', {
      method: 'POST',
      body: JSON.stringify({ email: email.value }),
    })
    resendMessage.value = data?.message || 'A new verification email is on its way.'
  } catch (err) {
    message.value = err.message
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
  margin-bottom: 18px;
}
form {
  display: grid;
  gap: 16px;
  margin-top: 14px;
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
  font-size: 0.95em;
  margin-bottom: 12px;
}
.success {
  color: #86efac;
  font-size: 0.95em;
  margin-bottom: 12px;
}
.info {
  color: var(--muted);
  font-size: 0.95em;
  line-height: 1.5;
}
.switch {
  color: var(--muted);
  margin-top: 18px;
  font-size: 0.92em;
}
</style>
