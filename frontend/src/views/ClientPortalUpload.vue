<template>
  <div class="portal-page">
    <main class="portal-shell">
      <section class="card upload-card">
        <header>
          <p class="brand">PhlowBooks</p>
          <h1 v-if="info">{{ info.client_name }}</h1>
          <p v-if="info?.label" class="label">{{ info.label }}</p>
        </header>

        <div v-if="loading" class="empty">Loading...</div>
        <div v-else-if="loadError" class="error">
          <strong>This link can't accept uploads right now.</strong>
          <p>{{ loadError }}</p>
        </div>
        <template v-else-if="info">
          <p class="instructions">
            Snap a photo of your receipt or invoice and upload here. JPEG, PNG, WebP, or PDF - up to {{ maxMb }} MB each.
          </p>

          <p v-if="info.uploads_remaining !== null" class="meta">
            {{ info.uploads_remaining }} upload{{ info.uploads_remaining === 1 ? '' : 's' }} remaining
            <span v-if="info.expires_at"> · expires {{ formatDate(info.expires_at) }}</span>
          </p>
          <p v-else-if="info.expires_at" class="meta">Expires {{ formatDate(info.expires_at) }}</p>

          <form @submit.prevent="upload">
            <label class="picker">
              <input
                ref="fileInput"
                type="file"
                multiple
                accept="image/jpeg,image/png,image/webp,application/pdf"
                capture="environment"
                @change="onFilesChange"
              />
              <span class="picker-cta">{{ files.length === 0 ? 'Choose files or take photo' : `${files.length} file${files.length === 1 ? '' : 's'} selected` }}</span>
            </label>
            <button type="submit" :disabled="files.length === 0 || uploading">
              {{ uploading ? 'Uploading...' : 'Upload' }}
            </button>
          </form>

          <div v-if="successCount" class="success">
            <strong>{{ successCount }} file{{ successCount === 1 ? '' : 's' }} uploaded.</strong>
            <p>Your bookkeeper will see them shortly. You can keep uploading more from this link.</p>
          </div>
          <p v-if="uploadError" class="error">{{ uploadError }}</p>
        </template>
      </section>

      <section v-if="info && !loadError" class="card receipt-card">
        <div class="section-head">
          <div>
            <p class="brand">Uploads</p>
            <h2>Your files</h2>
          </div>
          <button type="button" class="secondary" @click="loadReceipts">Refresh</button>
        </div>

        <div v-if="receiptsLoading" class="empty">Loading uploads...</div>
        <div v-else-if="receipts.length === 0" class="empty">No files uploaded through this link yet.</div>
        <div v-else class="receipt-list">
          <article
            v-for="receipt in receipts"
            :key="receipt.id"
            :class="['receipt-row', { active: selectedReceipt?.id === receipt.id }]"
          >
            <button type="button" @click="selectReceipt(receipt)">
              <span>
                <strong>{{ receipt.original_name || `Receipt #${receipt.id}` }}</strong>
                <small>{{ formatDate(receipt.created_at) }} · {{ receipt.status }}</small>
              </span>
              <em>{{ receipt.comment_count }} comment{{ receipt.comment_count === 1 ? '' : 's' }}</em>
            </button>
          </article>
        </div>
      </section>

      <section v-if="selectedReceipt" class="card thread-card">
        <div class="section-head">
          <div>
            <p class="brand">Clarifications</p>
            <h2>{{ selectedReceipt.original_name || `Receipt #${selectedReceipt.id}` }}</h2>
          </div>
          <button type="button" class="secondary" @click="selectedReceipt = null">Close</button>
        </div>

        <div v-if="commentsLoading" class="empty">Loading comments...</div>
        <div v-else class="thread">
          <p v-if="comments.length === 0" class="empty">No comments yet.</p>
          <article v-for="comment in comments" :key="comment.id" :class="['comment', comment.author_type]">
            <div>
              <strong>{{ comment.author_name }}</strong>
              <span>{{ comment.author_type === 'bookkeeper' ? 'Bookkeeper' : 'Client' }} · {{ formatDateTime(comment.created_at) }}</span>
            </div>
            <p>{{ comment.body }}</p>
          </article>
        </div>

        <form class="comment-form" @submit.prevent="postComment">
          <label>
            Name
            <input v-model="commentAuthor" type="text" maxlength="255" required />
          </label>
          <label>
            Comment
            <textarea v-model="commentBody" maxlength="2000" required placeholder="Ask a question or add context"></textarea>
          </label>
          <button type="submit" :disabled="postingComment">
            {{ postingComment ? 'Sending...' : 'Send comment' }}
          </button>
          <p v-if="commentError" class="error">{{ commentError }}</p>
        </form>
      </section>
    </main>
    <p class="footer">Secured by PhlowBooks · <router-link to="/">phlowbooks.app</router-link></p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { API_BASE_URL } from '../api'

const route = useRoute()
const token = route.params.token

const info = ref(null)
const loading = ref(true)
const loadError = ref('')
const files = ref([])
const uploading = ref(false)
const uploadError = ref('')
const successCount = ref(0)
const fileInput = ref(null)
const maxMb = 20

const receipts = ref([])
const receiptsLoading = ref(false)
const selectedReceipt = ref(null)
const comments = ref([])
const commentsLoading = ref(false)
const postingComment = ref(false)
const commentAuthor = ref(sessionStorage.getItem(`portal-comment-name:${token}`) || '')
const commentBody = ref('')
const commentError = ref('')

onMounted(async () => {
  try {
    await loadInfo()
    await loadReceipts()
  } catch (err) {
    loadError.value = err.message
  } finally {
    loading.value = false
  }
})

async function fetchPortal(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, options)
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new Error(data?.detail || 'Request failed.')
  return data
}

async function loadInfo() {
  info.value = await fetchPortal(`/portal/${token}`)
}

async function loadReceipts() {
  receiptsLoading.value = true
  try {
    const data = await fetchPortal(`/portal/${token}/receipts`)
    receipts.value = data.receipts || []
    if (selectedReceipt.value) {
      selectedReceipt.value = receipts.value.find((receipt) => receipt.id === selectedReceipt.value.id) || null
    }
  } finally {
    receiptsLoading.value = false
  }
}

function onFilesChange(event) {
  files.value = Array.from(event.target.files || [])
  successCount.value = 0
  uploadError.value = ''
}

async function upload() {
  if (files.value.length === 0) return
  uploading.value = true
  uploadError.value = ''
  successCount.value = 0
  try {
    const body = new FormData()
    files.value.forEach((file) => body.append('files', file))
    const res = await fetch(`${API_BASE_URL}/portal/${token}/upload`, { method: 'POST', body })
    const data = await res.json().catch(() => null)
    if (!res.ok) throw new Error(data?.detail || 'Upload failed.')
    successCount.value = data.receipts.length
    files.value = []
    if (fileInput.value) fileInput.value.value = ''
    await Promise.all([loadInfo(), loadReceipts()])
  } catch (err) {
    uploadError.value = err.message
  } finally {
    uploading.value = false
  }
}

async function selectReceipt(receipt) {
  selectedReceipt.value = receipt
  await loadComments(receipt)
}

async function loadComments(receipt = selectedReceipt.value) {
  if (!receipt) return
  commentsLoading.value = true
  commentError.value = ''
  try {
    const data = await fetchPortal(`/portal/${token}/receipts/${receipt.id}/comments`)
    comments.value = data.comments || []
  } catch (err) {
    commentError.value = err.message
  } finally {
    commentsLoading.value = false
  }
}

async function postComment() {
  if (!selectedReceipt.value) return
  postingComment.value = true
  commentError.value = ''
  try {
    await fetchPortal(`/portal/${token}/receipts/${selectedReceipt.value.id}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        author_name: commentAuthor.value,
        body: commentBody.value,
      }),
    })
    sessionStorage.setItem(`portal-comment-name:${token}`, commentAuthor.value)
    commentBody.value = ''
    await Promise.all([loadComments(), loadReceipts()])
  } catch (err) {
    commentError.value = err.message
  } finally {
    postingComment.value = false
  }
}

function formatDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleDateString()
}

function formatDateTime(value) {
  if (!value) return ''
  return new Date(value).toLocaleString()
}
</script>

<style scoped>
.portal-page {
  min-height: 100vh;
  background: #101827;
  color: #f1f5f9;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px 48px;
  gap: 24px;
}
.portal-shell {
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(280px, 440px) minmax(280px, 520px);
  width: min(980px, 100%);
}
.card {
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 8px;
  padding: 24px;
  display: grid;
  gap: 18px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.28);
}
.thread-card {
  grid-column: 2;
}
.brand {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.76em;
  color: #38bdf8;
  margin: 0;
}
h1,
h2 {
  margin: 4px 0 0;
}
h1 {
  font-size: 1.6em;
}
h2 {
  font-size: 1.1em;
}
.label,
.instructions {
  margin: 0;
  color: #e2e8f0;
}
.meta,
.empty,
.footer {
  margin: 0;
  color: #94a3b8;
}
form {
  display: grid;
  gap: 12px;
}
.picker {
  background: rgba(56, 189, 248, 0.08);
  border: 2px dashed rgba(56, 189, 248, 0.35);
  border-radius: 8px;
  padding: 22px;
  text-align: center;
  cursor: pointer;
  display: block;
}
.picker input {
  display: none;
}
.picker-cta {
  font-weight: 600;
  font-size: 1.02em;
}
button {
  background: #38bdf8;
  border: none;
  border-radius: 8px;
  color: #082f49;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  min-height: 42px;
  padding: 10px 14px;
}
button.secondary {
  background: rgba(148, 163, 184, 0.12);
  border: 1px solid rgba(148, 163, 184, 0.28);
  color: #e2e8f0;
  font-size: 0.9em;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.success,
.error {
  border-radius: 8px;
  padding: 12px 14px;
}
.success {
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.35);
}
.success p {
  margin: 4px 0 0;
  color: #bbf7d0;
  font-size: 0.92em;
}
.error {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.35);
  color: #fecaca;
}
.section-head {
  align-items: center;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.receipt-list {
  display: grid;
  gap: 8px;
}
.receipt-row button {
  align-items: center;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.18);
  color: #f1f5f9;
  display: flex;
  font-weight: 500;
  justify-content: space-between;
  min-height: 58px;
  text-align: left;
  width: 100%;
}
.receipt-row.active button,
.receipt-row button:hover {
  border-color: #38bdf8;
}
.receipt-row strong,
.receipt-row small {
  display: block;
}
.receipt-row small,
.receipt-row em {
  color: #94a3b8;
  font-size: 0.84em;
  font-style: normal;
}
.thread {
  display: grid;
  gap: 10px;
  max-height: 320px;
  overflow: auto;
}
.comment {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 8px;
  padding: 12px;
}
.comment.bookkeeper {
  border-color: rgba(56, 189, 248, 0.4);
}
.comment div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.comment span {
  color: #94a3b8;
  font-size: 0.8em;
}
.comment p {
  margin: 8px 0 0;
  white-space: pre-wrap;
}
.comment-form label {
  color: #94a3b8;
  display: grid;
  font-size: 0.78em;
  gap: 5px;
  text-transform: uppercase;
}
.comment-form input,
.comment-form textarea {
  background: #0f172a;
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 8px;
  color: #f1f5f9;
  font: inherit;
  padding: 10px;
  text-transform: none;
}
.comment-form textarea {
  min-height: 96px;
  resize: vertical;
}
.footer {
  font-size: 0.86em;
}
.footer a {
  color: #94a3b8;
}
@media (max-width: 820px) {
  .portal-shell {
    grid-template-columns: 1fr;
  }
  .thread-card {
    grid-column: auto;
  }
}
</style>
