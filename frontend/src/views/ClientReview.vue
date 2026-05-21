<template>
  <div class="review-page">
    <header class="review-header">
      <div>
        <p class="eyebrow">Review queue</p>
        <h1>{{ client?.name || 'Client' }}</h1>
      </div>
      <div class="header-actions">
        <span>{{ currentIndex + 1 || 0 }} of {{ queue.length }} remaining</span>
        <router-link :to="`/app/clients/${clientId}`">Back to client</router-link>
      </div>
    </header>

    <p v-if="error" class="error">{{ error }}</p>

    <section v-if="loading" class="empty">Loading review queue...</section>
    <section v-else-if="queue.length === 0" class="empty caught-up">
      <div class="caught-up-icon">✓</div>
      <h2>You're all caught up</h2>
      <p>No receipts need review right now. Upload more receipts when a new batch comes in, or check the archive for approved documents.</p>
      <div class="empty-actions">
        <router-link :to="`/app/clients/${clientId}`">Upload more receipts</router-link>
        <router-link :to="`/app/clients/${clientId}/archive`" class="secondary-link">Open archive</router-link>
      </div>
    </section>

    <section v-else class="review-shell">
      <aside class="queue-list">
        <button
          v-for="(receipt, index) in queue"
          :key="receipt.id"
          type="button"
          :class="{ active: receipt.id === currentReceipt?.id }"
          @click="selectReceipt(index)"
        >
          <strong>{{ receipt.original_name || `Receipt #${receipt.id}` }}</strong>
          <span :class="['status', receipt.status]">{{ receipt.status }}</span>
        </button>
      </aside>

      <main :class="['document-pane', { 'has-toolbar': canPreview(currentReceipt) }]">
        <div v-if="canPreview(currentReceipt)" class="document-toolbar">
          <template v-if="isPdf(currentReceipt)">
            <button type="button" :disabled="pdfPage <= 1" @click="changePdfPage(pdfPage - 1)">Prev</button>
            <span class="page-count">Page {{ pdfPage }} / {{ pdfPageCount || '?' }}</span>
            <button
              type="button"
              :disabled="pdfPageCount && pdfPage >= pdfPageCount"
              @click="changePdfPage(pdfPage + 1)"
            >
              Next
            </button>
          </template>
          <button type="button" @click="zoom = Math.max(0.5, zoom - 0.1)">-</button>
          <span>{{ Math.round(zoom * 100) }}%</span>
          <button type="button" @click="zoom = Math.min(2, zoom + 0.1)">+</button>
          <button
            v-if="currentReceipt?.status === 'error'"
            type="button"
            :disabled="reprocessing"
            @click="reprocessCurrent"
          >
            {{ reprocessing ? 'Retrying...' : 'Retry OCR' }}
          </button>
        </div>
        <div class="document-view">
          <img
            v-if="canPreview(currentReceipt) && previewObjectUrl"
            :src="previewObjectUrl"
            :style="{ transform: `scale(${zoom})` }"
            alt="Uploaded receipt"
          />
          <div v-else class="pdf-placeholder">
            <h2>Preview unavailable</h2>
            <p>This file type cannot be previewed in the browser.</p>
          </div>
        </div>
      </main>

      <form class="fields-pane" @submit.prevent="approve">
        <div class="form-head">
          <div>
            <h2>Extracted fields</h2>
            <p>{{ currentReceipt?.original_name }}</p>
          </div>
          <span :class="['confidence', confidenceClass]">{{ confidenceLabel }}</span>
        </div>
        <p v-if="currentReceipt?.error_message" class="extraction-note">
          {{ currentReceipt.error_message }}
        </p>

        <label :class="fieldClass">
          Vendor
          <input v-model="form.vendor" type="text" />
        </label>
        <label :class="fieldClass">
          Vendor TIN
          <input v-model="form.vendor_tin" type="text" placeholder="000-000-000-00000" />
        </label>
        <div class="two-col">
          <label :class="fieldClass">
            OR number
            <input v-model="form.or_number" type="text" />
          </label>
          <label :class="fieldClass">
            SI number
            <input v-model="form.si_number" type="text" />
          </label>
        </div>
        <label :class="fieldClass">
          ATP number
          <input v-model="form.atp_number" type="text" />
        </label>
        <div class="two-col">
          <label :class="fieldClass">
            Date
            <input v-model="form.date" type="date" />
          </label>
          <label :class="fieldClass">
            Document type
            <select v-model="form.doc_type">
              <option value="">Unknown</option>
              <option value="official_receipt">Official receipt</option>
              <option value="sales_invoice">Sales invoice</option>
              <option value="gcash">GCash</option>
              <option value="maya">Maya</option>
              <option value="bank_statement">Bank statement</option>
              <option value="other">Other</option>
            </select>
          </label>
        </div>
        <div class="two-col">
          <label :class="fieldClass">
            VAT type
            <select v-model="form.vat_type">
              <option value="">Unknown</option>
              <option value="vatable">Vatable</option>
              <option value="zero_rated">Zero-rated</option>
              <option value="exempt">Exempt</option>
              <option value="non_vat">Non-VAT</option>
            </select>
          </label>
          <label :class="fieldClass">
            Currency
            <input v-model="form.currency" type="text" maxlength="3" />
          </label>
        </div>
        <div class="two-col">
          <label :class="fieldClass">
            Vatable amount
            <input v-model.number="form.vatable_amount" type="number" step="0.01" />
          </label>
          <label :class="fieldClass">
            VAT amount
            <input v-model.number="form.vat_amount" type="number" step="0.01" />
          </label>
        </div>
        <p v-if="vatSanity.status === 'warning'" class="vat-warning">
          {{ vatSanity.message }}
        </p>
        <div class="two-col">
          <label :class="fieldClass">
            Subtotal
            <input v-model.number="form.subtotal" type="number" step="0.01" />
          </label>
          <label :class="fieldClass">
            Total
            <input v-model.number="form.total" type="number" step="0.01" />
          </label>
        </div>

        <label>
          Raw OCR text
          <textarea :value="currentReceipt?.raw_text || ''" readonly rows="5" />
        </label>

        <div class="form-actions">
          <button type="button" class="secondary" @click="reject">Reject</button>
          <button type="submit">Approve</button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch, apiFetchBlobWithHeaders, clearToken } from '../api'

const route = useRoute()
const router = useRouter()
const clientId = route.params.id
const client = ref(null)
const queue = ref([])
const currentIndex = ref(0)
const loading = ref(true)
const error = ref('')
const zoom = ref(1)
const reprocessing = ref(false)
const previewObjectUrl = ref('')
const pdfPage = ref(1)
const pdfPageCount = ref(null)
let previewRequestId = 0

const form = reactive(emptyForm())

const currentReceipt = computed(() => queue.value[currentIndex.value] || null)
const confidence = computed(() => currentReceipt.value?.data?.confidence ?? null)
const confidenceLabel = computed(() => {
  if (confidence.value === null) return 'No confidence score'
  return `${Math.round(confidence.value * 100)}% confidence`
})
const confidenceClass = computed(() => {
  if (confidence.value === null) return 'unknown'
  if (confidence.value < 0.75) return 'low'
  if (confidence.value < 0.9) return 'medium'
  return 'high'
})
const fieldClass = computed(() => ({
  caution: confidence.value !== null && confidence.value < 0.9,
  danger: confidence.value !== null && confidence.value < 0.75,
}))
const vatSanity = computed(() => calculateVatSanity(form))

onMounted(async () => {
  await loadQueue()
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  releasePreview()
})

watch(currentReceipt, (receipt) => {
  pdfPage.value = 1
  pdfPageCount.value = null
  loadPreview(receipt)
})

async function loadQueue() {
  loading.value = true
  error.value = ''
  try {
    const [clientData, queueData] = await Promise.all([
      apiFetch(`/clients/${clientId}`),
      apiFetch(`/clients/${clientId}/receipts/queue`),
    ])
    client.value = clientData
    queue.value = queueData.receipts
    currentIndex.value = 0
    syncForm()
  } catch (err) {
    if (err.message.includes('credentials')) {
      clearToken()
      router.push('/login')
      return
    }
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function emptyForm() {
  return {
    vendor: '',
    vendor_tin: '',
    or_number: '',
    si_number: '',
    atp_number: '',
    date: '',
    currency: 'PHP',
    subtotal: null,
    tax: null,
    vat_type: '',
    vatable_amount: null,
    vat_amount: null,
    total: null,
    doc_type: '',
    confidence: null,
  }
}

function syncForm() {
  Object.assign(form, emptyForm(), currentReceipt.value?.data || {})
}

function selectReceipt(index) {
  currentIndex.value = index
  zoom.value = 1
  pdfPage.value = 1
  pdfPageCount.value = null
  syncForm()
}

function releasePreview() {
  if (previewObjectUrl.value) {
    URL.revokeObjectURL(previewObjectUrl.value)
    previewObjectUrl.value = ''
  }
}

async function loadPreview(receipt) {
  releasePreview()
  if (!receipt || !canPreview(receipt)) return
  const requestId = ++previewRequestId
  try {
    const pageQuery = isPdf(receipt) ? `?page=${pdfPage.value}` : ''
    const { blob, headers } = await apiFetchBlobWithHeaders(`/receipts/${receipt.id}/preview${pageQuery}`)
    const url = URL.createObjectURL(blob)
    if (requestId !== previewRequestId) {
      URL.revokeObjectURL(url)
      return
    }
    const pageCount = Number(headers.get('X-PDF-Page-Count') || 0)
    pdfPageCount.value = pageCount || null
    previewObjectUrl.value = url
  } catch (err) {
    if (requestId === previewRequestId) {
      error.value = err.message || 'Could not load preview'
    }
  }
}

async function changePdfPage(page) {
  if (!currentReceipt.value || !isPdf(currentReceipt.value)) return
  if (page < 1) return
  if (pdfPageCount.value && page > pdfPageCount.value) return
  pdfPage.value = page
  await loadPreview(currentReceipt.value)
}

function isImage(receipt) {
  return receipt?.mime_type?.startsWith('image/')
}

function isPdf(receipt) {
  return receipt?.mime_type === 'application/pdf'
}

function canPreview(receipt) {
  return isImage(receipt) || isPdf(receipt)
}

async function approve() {
  await saveReceipt('approved')
}

async function reject() {
  await saveReceipt('rejected')
}

async function reprocessCurrent() {
  if (!currentReceipt.value) return
  reprocessing.value = true
  error.value = ''
  try {
    const updated = await apiFetch(`/receipts/${currentReceipt.value.id}/reprocess`, {
      method: 'POST',
    })
    queue.value[currentIndex.value] = updated
    syncForm()
  } catch (err) {
    error.value = err.message
  } finally {
    reprocessing.value = false
  }
}

async function saveReceipt(status) {
  if (!currentReceipt.value) return
  error.value = ''
  try {
    await apiFetch(`/receipts/${currentReceipt.value.id}`, {
      method: 'PATCH',
      body: JSON.stringify({
        status,
        data: normalizeForm(),
      }),
    })
    queue.value.splice(currentIndex.value, 1)
    if (currentIndex.value >= queue.value.length) {
      currentIndex.value = Math.max(0, queue.value.length - 1)
    }
    syncForm()
  } catch (err) {
    error.value = err.message
  }
}

function normalizeForm() {
  const data = { ...form }
  for (const key of Object.keys(data)) {
    if (data[key] === '') data[key] = null
  }
  data.currency = data.currency || 'PHP'
  data.confidence = confidence.value
  return data
}

function calculateVatSanity(data) {
  const vatable = Number(data.vatable_amount)
  const vat = Number(data.vat_amount)
  if (!Number.isFinite(vatable) || !Number.isFinite(vat)) return { status: null, message: '' }
  if (['zero_rated', 'exempt', 'non_vat'].includes(data.vat_type) && vat === 0) {
    return { status: null, message: '' }
  }
  const expected = Math.round(vatable * 0.12 * 100) / 100
  const difference = Math.round((vat - expected) * 100) / 100
  if (Math.abs(difference) <= 1) return { status: 'ok', message: '' }
  return {
    status: 'warning',
    message: `VAT check: expected around ${formatPlainAmount(expected)}, captured ${formatPlainAmount(vat)} (${difference >= 0 ? '+' : ''}${formatPlainAmount(difference)}).`,
  }
}

function formatPlainAmount(value) {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: form.currency || 'PHP',
  }).format(value)
}

function onKeydown(event) {
  if (event.key === 'Enter' && event.target?.tagName !== 'TEXTAREA') {
    event.preventDefault()
    approve()
  }
}
</script>

<style scoped>
.review-page {
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  height: 100%;
  overflow: hidden;
  overscroll-behavior: none;
  padding: 0 24px;
}
.review-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  margin: 0 auto 10px;
  max-width: 1440px;
  width: 100%;
}
.review-header h1 {
  font-size: 1.55em;
}
.eyebrow {
  color: var(--workflow-eyebrow);
  font-size: 0.78em;
  font-weight: 700;
  letter-spacing: 0;
  margin-bottom: 2px;
  text-transform: uppercase;
}
.header-actions {
  display: flex;
  gap: 16px;
  align-items: center;
  color: var(--workflow-muted);
}
.review-shell {
  display: grid;
  grid-template-columns: 220px minmax(420px, 1fr) minmax(340px, 460px);
  gap: 16px;
  max-width: 1440px;
  margin: 0 auto;
  min-height: 0;
  width: 100%;
}
.queue-list,
.document-pane,
.fields-pane,
.empty {
  background: linear-gradient(180deg, var(--workflow-panel-strong), var(--workflow-panel));
  border: 1px solid var(--workflow-line);
  border-radius: 10px;
  box-shadow: var(--workflow-panel-shadow);
}
.queue-list {
  display: grid;
  align-content: start;
  gap: 8px;
  overflow: auto;
  overscroll-behavior: contain;
  padding: 12px;
}
.queue-list button {
  background: var(--workflow-input);
  border: 1px solid var(--workflow-soft-line);
  border-radius: 8px;
  color: var(--workflow-text);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  padding: 12px;
  text-align: left;
  width: 100%;
}
.queue-list strong {
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  overflow-wrap: anywhere;
  text-overflow: ellipsis;
}
.queue-list button.active {
  background: rgba(124, 58, 237, 0.16);
  border-color: rgba(167, 139, 250, 0.42);
}
.queue-list button:hover {
  border-color: rgba(147, 197, 253, 0.28);
}
.status,
.confidence {
  border-radius: 999px;
  display: inline-flex;
  font-size: 0.78em;
  padding: 3px 8px;
  width: fit-content;
}
.status.pending,
.status.processing,
.confidence.medium {
  background: rgba(250, 204, 21, 0.14);
  color: #fde68a;
}
.status.done,
.status.approved,
.confidence.high {
  background: rgba(34, 197, 94, 0.14);
  color: #86efac;
}
.status.error,
.status.rejected,
.confidence.low {
  background: rgba(248, 113, 113, 0.14);
  color: #fca5a5;
}
.confidence.unknown {
  background: rgba(148, 163, 184, 0.08);
  color: var(--workflow-muted);
}
.document-pane {
  display: grid;
  grid-template-rows: minmax(0, 1fr);
  overflow: hidden;
  overscroll-behavior: contain;
}
.document-pane.has-toolbar {
  grid-template-rows: auto minmax(0, 1fr);
}
.document-toolbar {
  border-bottom: 1px solid var(--workflow-line);
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
}
.page-count {
  color: var(--workflow-text);
  font-weight: 600;
  min-width: 88px;
  text-align: center;
}
button {
  border: 1px solid var(--workflow-line);
  border-radius: 8px;
  background: rgba(148, 163, 184, 0.08);
  color: var(--workflow-text);
  cursor: pointer;
  font: inherit;
  padding: 8px 12px;
}
button:hover:not(:disabled) {
  background: rgba(148, 163, 184, 0.14);
  border-color: rgba(167, 139, 250, 0.52);
}
.document-view {
  display: grid;
  align-items: start;
  justify-items: center;
  min-height: 0;
  overflow: auto;
  overscroll-behavior: contain;
  padding: 12px;
}
.document-view img {
  max-width: 100%;
  max-height: none;
  transform-origin: top center;
  transition: transform 0.12s ease;
}
.pdf-placeholder {
  max-width: 420px;
  text-align: center;
}
.pdf-placeholder h2 {
  margin-bottom: 8px;
}
.pdf-placeholder p {
  color: var(--workflow-muted);
  margin-bottom: 14px;
}
.fields-pane {
  display: grid;
  gap: 14px;
  align-content: start;
  overflow: auto;
  overscroll-behavior: contain;
  padding: 18px;
}
.form-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: start;
}
.form-head h2 {
  font-size: 1.1em;
}
.form-head p {
  color: var(--workflow-muted);
  font-size: 0.9em;
}
.extraction-note,
.vat-warning {
  background: rgba(250, 204, 21, 0.09);
  border: 1px solid rgba(250, 204, 21, 0.24);
  border-radius: 8px;
  color: #fde68a;
  font-size: 0.9em;
  padding: 10px 12px;
}
label {
  color: var(--workflow-muted);
  display: grid;
  gap: 5px;
  font-size: 0.88em;
}
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
input,
select,
textarea {
  border: 1px solid var(--workflow-line);
  border-radius: 8px;
  background: var(--workflow-input);
  color: var(--workflow-text);
  font: inherit;
  padding: 10px 12px;
}
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline-color: var(--workflow-accent-2);
}
label.caution input,
label.caution select {
  border-color: #ca8a04;
}
label.danger input,
label.danger select {
  border-color: #ef4444;
}
textarea {
  resize: vertical;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.form-actions button[type="submit"] {
  background: linear-gradient(135deg, var(--workflow-accent), #5b5df6);
  border-color: transparent;
  color: white;
  font-weight: 600;
}
.form-actions button[type="submit"]:hover:not(:disabled) {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
}
.secondary {
  color: #fca5a5;
}
.empty {
  color: var(--workflow-muted);
  margin: 40px auto;
  max-width: 720px;
  padding: 28px;
}
.caught-up {
  align-self: start;
  margin-top: 72px;
  max-width: 520px;
  text-align: center;
}
.caught-up-icon {
  align-items: center;
  background: rgba(34, 197, 94, 0.14);
  border: 1px solid rgba(134, 239, 172, 0.28);
  border-radius: 999px;
  color: #86efac;
  display: inline-flex;
  font-size: 1.25em;
  font-weight: 700;
  height: 42px;
  justify-content: center;
  margin-bottom: 14px;
  width: 42px;
}
.caught-up h2 {
  color: var(--workflow-text);
  font-size: 1.35em;
  margin-bottom: 8px;
}
.caught-up p {
  margin: 0 auto 18px;
  max-width: 420px;
}
.empty-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}
.empty-actions a {
  background: linear-gradient(135deg, var(--workflow-accent), #5b5df6);
  border: 1px solid transparent;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  padding: 9px 13px;
}
.empty-actions .secondary-link {
  background: rgba(148, 163, 184, 0.08);
  border-color: var(--workflow-line);
  color: var(--workflow-text);
}
.error {
  color: #fca5a5;
  margin: 0 auto 16px;
  max-width: 1440px;
}
@media (max-width: 1100px) {
  .review-page {
    height: auto;
    margin-top: 0;
    overflow: visible;
  }
  .review-shell {
    grid-template-columns: 1fr;
  }
  .queue-list {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
}
@media (max-width: 640px) {
  .review-header,
  .header-actions,
  .two-col {
    align-items: flex-start;
    flex-direction: column;
    grid-template-columns: 1fr;
  }
}
</style>
