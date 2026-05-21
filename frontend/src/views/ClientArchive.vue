<template>
  <div class="container archive-page">
    <header>
      <div>
        <p class="eyebrow">Archive</p>
        <h1>{{ client?.name || 'Receipts' }}</h1>
      </div>
      <router-link :to="`/app/clients/${clientId}`">Back to client</router-link>
    </header>

    <section class="filters">
      <label>
        Month
        <input v-model="filters.month" type="month" />
      </label>
      <label>
        Vendor
        <input v-model="filters.vendor" type="search" placeholder="Vendor name" />
      </label>
      <label>
        Document type
        <select v-model="filters.doc_type">
          <option value="">All</option>
          <option value="official_receipt">Official receipt</option>
          <option value="sales_invoice">Sales invoice</option>
          <option value="gcash">GCash</option>
          <option value="maya">Maya</option>
          <option value="bank_statement">Bank statement</option>
          <option value="other">Other</option>
        </select>
      </label>
      <label>
        VAT type
        <select v-model="filters.vat_type">
          <option value="">All</option>
          <option value="vatable">Vatable</option>
          <option value="zero_rated">Zero-rated</option>
          <option value="exempt">Exempt</option>
          <option value="non_vat">Non-VAT</option>
        </select>
      </label>
      <label>
        Min amount
        <input v-model="filters.min_total" type="number" step="0.01" />
      </label>
      <label>
        Max amount
        <input v-model="filters.max_total" type="number" step="0.01" />
      </label>
      <div class="filter-actions">
        <button type="button" @click="loadArchive">Apply</button>
        <button type="button" class="secondary" @click="resetFilters">Reset</button>
      </div>
    </section>

    <p v-if="error" class="error">{{ error }}</p>

    <section class="summary">
      <div>
        <span>Approved receipts</span>
        <strong>{{ receipts.length }}</strong>
      </div>
      <div>
        <span>Total amount</span>
        <strong>{{ formatAmount(totalAmount) }}</strong>
      </div>
      <div>
        <span>Low confidence</span>
        <strong>{{ lowConfidenceCount }}</strong>
      </div>
      <div>
        <span>VAT warnings</span>
        <strong>{{ vatWarningCount }}</strong>
      </div>
    </section>

    <section class="export-panel">
      <div>
        <p class="eyebrow">Export</p>
        <h2>Download approved receipts</h2>
        <p>Exports use the same filters currently applied to the archive.</p>
      </div>
      <div class="export-actions">
        <select v-model="exportFormat" aria-label="Export format">
          <option value="generic">Generic CSV</option>
          <option value="qbo">QuickBooks CSV</option>
          <option value="xero">Xero CSV</option>
        </select>
        <button type="button" @click="downloadExport">Download CSV</button>
      </div>
    </section>

    <section class="archive-list">
      <div class="section-head">
        <h2>Approved documents</h2>
        <router-link :to="`/app/clients/${clientId}/review`">Open review queue</router-link>
      </div>

      <div v-if="loading" class="empty">Loading archive...</div>
      <div v-else-if="receipts.length === 0" class="empty">No approved receipts match these filters.</div>
      <table v-else>
        <thead>
          <tr>
            <th>Date</th>
            <th>Vendor</th>
            <th>TIN</th>
            <th>Reference</th>
            <th>Doc type</th>
            <th>VAT</th>
            <th>Total</th>
            <th>Checks</th>
            <th>Confidence</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="receipt in receipts" :key="receipt.id" :class="{ selected: selectedReceipt?.id === receipt.id }">
            <td>{{ receipt.data?.date || '-' }}</td>
            <td>
              <strong>{{ receipt.data?.vendor || receipt.original_name || `Receipt #${receipt.id}` }}</strong>
              <span>{{ receipt.original_name }}</span>
            </td>
            <td>{{ receipt.data?.vendor_tin || '-' }}</td>
            <td>{{ receipt.data?.or_number || receipt.data?.si_number || '-' }}</td>
            <td>{{ label(receipt.data?.doc_type) }}</td>
            <td>{{ label(receipt.data?.vat_type) }}</td>
            <td>{{ formatAmount(receipt.data?.total, receipt.data?.currency) }}</td>
            <td>
              <span :class="['check-pill', vatCheckClass(receipt.data)]">
                {{ vatCheckLabel(receipt.data) }}
              </span>
            </td>
            <td>
              <span :class="['confidence', confidenceClass(receipt.data?.confidence)]">
                {{ formatConfidence(receipt.data?.confidence) }}
              </span>
            </td>
            <td>
              <button type="button" class="secondary compact" @click="openReceipt(receipt)">View</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <div
      v-if="selectedReceipt"
      class="detail-overlay"
      role="presentation"
      @click.self="closeReceipt"
    >
      <section class="detail-panel" role="dialog" aria-modal="true" aria-labelledby="receipt-detail-title">
        <div class="detail-head">
          <div>
            <p class="eyebrow">Read-only detail</p>
            <h2 id="receipt-detail-title">
              {{ selectedReceipt.data?.vendor || selectedReceipt.original_name || `Receipt #${selectedReceipt.id}` }}
            </h2>
            <p>{{ selectedReceipt.original_name }} - {{ selectedReceipt.status }}</p>
          </div>
          <button type="button" class="secondary" @click="closeReceipt">Close</button>
        </div>

        <div class="detail-grid">
          <aside class="document-preview">
            <div v-if="canPreview(selectedReceipt)" class="preview-toolbar">
              <template v-if="isPdf(selectedReceipt)">
                <button type="button" class="secondary compact" :disabled="previewPage <= 1" @click="changePreviewPage(previewPage - 1)">
                  Prev
                </button>
                <span class="page-count">Page {{ previewPage }} / {{ previewPageCount || '?' }}</span>
                <button
                  type="button"
                  class="secondary compact"
                  :disabled="previewPageCount && previewPage >= previewPageCount"
                  @click="changePreviewPage(previewPage + 1)"
                >
                  Next
                </button>
              </template>
              <button type="button" class="secondary compact" @click="previewZoom = Math.max(0.5, previewZoom - 0.1)">
                -
              </button>
              <span>{{ Math.round(previewZoom * 100) }}%</span>
              <button type="button" class="secondary compact" @click="previewZoom = Math.min(2, previewZoom + 0.1)">
                +
              </button>
            </div>
            <div class="preview-canvas">
              <img
                v-if="canPreview(selectedReceipt) && previewObjectUrl"
                :src="previewObjectUrl"
                :style="{ width: `${previewZoom * 100}%` }"
                alt="Archived receipt"
              />
              <div v-else class="pdf-placeholder">
                <h3>Preview unavailable</h3>
                <p>This file type cannot be previewed in the browser.</p>
              </div>
            </div>
          </aside>

          <div class="detail-content">
            <dl class="field-grid">
              <div>
                <dt>Date</dt>
                <dd>{{ selectedReceipt.data?.date || '-' }}</dd>
              </div>
              <div>
                <dt>Vendor TIN</dt>
                <dd>{{ selectedReceipt.data?.vendor_tin || '-' }}</dd>
              </div>
              <div>
                <dt>OR number</dt>
                <dd>{{ selectedReceipt.data?.or_number || '-' }}</dd>
              </div>
              <div>
                <dt>SI number</dt>
                <dd>{{ selectedReceipt.data?.si_number || '-' }}</dd>
              </div>
              <div>
                <dt>ATP number</dt>
                <dd>{{ selectedReceipt.data?.atp_number || '-' }}</dd>
              </div>
              <div>
                <dt>Document type</dt>
                <dd>{{ label(selectedReceipt.data?.doc_type) }}</dd>
              </div>
              <div>
                <dt>VAT type</dt>
                <dd>{{ label(selectedReceipt.data?.vat_type) }}</dd>
              </div>
              <div>
                <dt>Vatable amount</dt>
                <dd>{{ formatAmount(selectedReceipt.data?.vatable_amount, selectedReceipt.data?.currency) }}</dd>
              </div>
              <div>
                <dt>VAT amount</dt>
                <dd>{{ formatAmount(selectedReceipt.data?.vat_amount, selectedReceipt.data?.currency) }}</dd>
              </div>
              <div>
                <dt>VAT check</dt>
                <dd>
                  <span :class="['check-pill', vatCheckClass(selectedReceipt.data)]">
                    {{ vatCheckLabel(selectedReceipt.data) }}
                  </span>
                  <span v-if="selectedReceipt.data?.vat_sanity_message" class="check-message">
                    {{ selectedReceipt.data.vat_sanity_message }}
                  </span>
                </dd>
              </div>
              <div>
                <dt>Subtotal</dt>
                <dd>{{ formatAmount(selectedReceipt.data?.subtotal, selectedReceipt.data?.currency) }}</dd>
              </div>
              <div>
                <dt>Total</dt>
                <dd>{{ formatAmount(selectedReceipt.data?.total, selectedReceipt.data?.currency) }}</dd>
              </div>
              <div>
                <dt>Confidence</dt>
                <dd>{{ formatConfidence(selectedReceipt.data?.confidence) }}</dd>
              </div>
              <div>
                <dt>Processed</dt>
                <dd>{{ formatDateTime(selectedReceipt.processed_at) }}</dd>
              </div>
            </dl>

            <section class="line-items">
              <h3>Line items</h3>
              <div v-if="selectedReceipt.line_items.length === 0" class="empty">No line items captured.</div>
              <table v-else>
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Qty</th>
                    <th>Unit</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in selectedReceipt.line_items" :key="item.id">
                    <td>{{ item.description }}</td>
                    <td>{{ item.quantity ?? '-' }}</td>
                    <td>{{ formatAmount(item.unit_price, selectedReceipt.data?.currency) }}</td>
                    <td>{{ formatAmount(item.total, selectedReceipt.data?.currency) }}</td>
                  </tr>
                </tbody>
              </table>
            </section>

            <section class="audit-log">
              <h3>Audit history</h3>
              <div v-if="loadingAuditLogs" class="empty">Loading audit history...</div>
              <div v-else-if="auditLogs.length === 0" class="empty">No manual field edits recorded.</div>
              <table v-else>
                <thead>
                  <tr>
                    <th>When</th>
                    <th>Who</th>
                    <th>Field</th>
                    <th>Old</th>
                    <th>New</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="entry in auditLogs" :key="entry.id">
                    <td>{{ formatDateTime(entry.created_at) }}</td>
                    <td>{{ entry.actor_name || `User #${entry.user_id}` }}</td>
                    <td>{{ formatAuditField(entry.field_name) }}</td>
                    <td>{{ formatAuditValue(entry.old_value) }}</td>
                    <td>{{ formatAuditValue(entry.new_value) }}</td>
                  </tr>
                </tbody>
              </table>
            </section>

            <section class="raw-text">
              <h3>Raw OCR text</h3>
              <textarea :value="selectedReceipt.raw_text || 'No OCR text captured.'" readonly rows="8" />
            </section>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { API_BASE_URL, apiFetch, apiFetchBlobWithHeaders, clearToken, getToken } from '../api'

const route = useRoute()
const router = useRouter()
const clientId = route.params.id
const client = ref(null)
const receipts = ref([])
const selectedReceipt = ref(null)
const auditLogs = ref([])
const loading = ref(true)
const loadingAuditLogs = ref(false)
const error = ref('')
const exportFormat = ref('generic')
const previewZoom = ref(1)
const previewObjectUrl = ref('')
const previewPage = ref(1)
const previewPageCount = ref(null)
let previewRequestId = 0
const filters = reactive(defaultFilters())

const totalAmount = computed(() =>
  receipts.value.reduce((sum, receipt) => sum + Number(receipt.data?.total || 0), 0)
)
const lowConfidenceCount = computed(() =>
  receipts.value.filter((receipt) => receipt.data?.confidence !== null && receipt.data?.confidence < 0.9).length
)
const vatWarningCount = computed(() =>
  receipts.value.filter((receipt) => receipt.data?.vat_sanity_status === 'warning').length
)

onMounted(async () => {
  try {
    client.value = await apiFetch(`/clients/${clientId}`)
    await loadArchive()
  } catch (err) {
    handleError(err)
  }
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
  releasePreview()
})

watch(selectedReceipt, (receipt) => {
  document.body.style.overflow = receipt ? 'hidden' : ''
  previewPage.value = 1
  previewPageCount.value = null
  loadPreview(receipt)
})

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
    const pageQuery = isPdf(receipt) ? `?page=${previewPage.value}` : ''
    const { blob, headers } = await apiFetchBlobWithHeaders(`/receipts/${receipt.id}/preview${pageQuery}`)
    const url = URL.createObjectURL(blob)
    if (requestId !== previewRequestId) {
      URL.revokeObjectURL(url)
      return
    }
    const pageCount = Number(headers.get('X-PDF-Page-Count') || 0)
    previewPageCount.value = pageCount || null
    previewObjectUrl.value = url
  } catch (err) {
    if (requestId === previewRequestId) {
      handleError(err)
    }
  }
}

async function changePreviewPage(page) {
  if (!selectedReceipt.value || !isPdf(selectedReceipt.value)) return
  if (page < 1) return
  if (previewPageCount.value && page > previewPageCount.value) return
  previewPage.value = page
  await loadPreview(selectedReceipt.value)
}

function defaultFilters() {
  return {
    month: '',
    vendor: '',
    doc_type: '',
    vat_type: '',
    min_total: '',
    max_total: '',
  }
}

async function loadArchive() {
  loading.value = true
  error.value = ''
  try {
    const params = buildFilterParams()
    params.set('status', 'approved')
    const data = await apiFetch(`/clients/${clientId}/receipts?${params.toString()}`)
    receipts.value = data.receipts
    if (selectedReceipt.value && !receipts.value.some((receipt) => receipt.id === selectedReceipt.value.id)) {
      selectedReceipt.value = null
    }
  } catch (err) {
    handleError(err)
  } finally {
    loading.value = false
  }
}

async function openReceipt(receipt) {
  error.value = ''
  previewZoom.value = 1
  previewPage.value = 1
  previewPageCount.value = null
  loadingAuditLogs.value = true
  try {
    const [receiptData, auditData] = await Promise.all([
      apiFetch(`/receipts/${receipt.id}`),
      apiFetch(`/receipts/${receipt.id}/audit-logs`),
    ])
    auditLogs.value = auditData.audit_logs || []
    selectedReceipt.value = receiptData
  } catch (err) {
    handleError(err)
  } finally {
    loadingAuditLogs.value = false
  }
}

function closeReceipt() {
  selectedReceipt.value = null
  auditLogs.value = []
}

function onKeydown(event) {
  if (event.key === 'Escape' && selectedReceipt.value) {
    closeReceipt()
  }
}

function resetFilters() {
  Object.assign(filters, defaultFilters())
  loadArchive()
}

async function downloadExport() {
  error.value = ''
  try {
    const params = buildFilterParams()
    params.set('format', exportFormat.value)
    const res = await fetch(`${API_BASE_URL}/clients/${clientId}/export?${params.toString()}`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    if (!res.ok) {
      const data = await res.json().catch(() => null)
      throw new Error(data?.detail || 'Export failed')
    }

    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = exportFilename()
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  } catch (err) {
    handleError(err)
  }
}

function buildFilterParams() {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== '') params.set(key, value)
  }
  return params
}

function exportFilename() {
  const month = filters.month || 'all'
  return `phlowbooks-${clientId}-${exportFormat.value}-${month}.csv`
}

function handleError(err) {
  if (err.message.includes('credentials')) {
    clearToken()
    router.push('/login')
    return
  }
  error.value = err.message
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

function label(value) {
  if (!value) return '-'
  return value.replaceAll('_', ' ')
}

function formatAmount(value, currency = 'PHP') {
  if (value === null || value === undefined) return '-'
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: currency || 'PHP',
  }).format(value)
}

function formatConfidence(value) {
  if (value === null || value === undefined) return '-'
  return `${Math.round(value * 100)}%`
}

function formatDateTime(value) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('en-PH', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function confidenceClass(value) {
  if (value === null || value === undefined) return 'unknown'
  if (value < 0.75) return 'low'
  if (value < 0.9) return 'medium'
  return 'high'
}

function vatCheckClass(data) {
  if (data?.vat_sanity_status === 'warning') return 'warning'
  if (data?.vat_sanity_status === 'ok') return 'ok'
  return 'neutral'
}

function vatCheckLabel(data) {
  if (data?.vat_sanity_status === 'warning') return 'VAT warning'
  if (data?.vat_sanity_status === 'ok') return 'VAT OK'
  return '-'
}

function formatAuditField(fieldName) {
  return fieldName.replace(/^receipt_data\./, '').replace(/^receipt\./, '').replaceAll('_', ' ')
}

function formatAuditValue(value) {
  if (value === null || value === undefined || value === '') return '-'
  return value
}
</script>

<style scoped>
.archive-page {
  padding: 16px 24px 64px;
}
header {
  align-items: center;
  display: flex;
  gap: 20px;
  justify-content: space-between;
  margin-bottom: 24px;
}
.eyebrow {
  color: var(--workflow-eyebrow);
  font-size: 0.78em;
  font-weight: 700;
  letter-spacing: 0;
  margin-bottom: 4px;
  text-transform: uppercase;
}
.filters,
.summary,
.export-panel,
.archive-list,
.detail-panel {
  background: linear-gradient(180deg, var(--workflow-panel-strong), var(--workflow-panel));
  border: 1px solid var(--workflow-line);
  border-radius: 10px;
  box-shadow: var(--workflow-panel-shadow);
  padding: 18px;
}
.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 14px;
  margin-bottom: 18px;
}
label {
  color: var(--workflow-muted);
  display: grid;
  gap: 6px;
  font-size: 0.88em;
}
input,
select {
  background: var(--workflow-input);
  border: 1px solid var(--workflow-line);
  border-radius: 8px;
  color: var(--workflow-text);
  font: inherit;
  padding: 10px 12px;
}
input:focus-visible,
select:focus-visible {
  outline-color: var(--workflow-accent-2);
}
.filter-actions {
  align-items: end;
  display: flex;
  gap: 8px;
}
button {
  background: linear-gradient(135deg, var(--workflow-accent), #5b5df6);
  border: 1px solid transparent;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
  padding: 10px 14px;
}
button:hover:not(:disabled) {
  background: linear-gradient(135deg, #8b5cf6, #6366f1);
}
button.secondary {
  background: rgba(148, 163, 184, 0.08);
  border-color: var(--workflow-line);
  color: var(--workflow-text);
}
button.secondary:hover:not(:disabled) {
  background: rgba(148, 163, 184, 0.14);
  border-color: rgba(167, 139, 250, 0.52);
}
button.compact {
  padding: 7px 10px;
}
.summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 18px;
}
.summary div {
  background: var(--workflow-input);
  border: 1px solid var(--workflow-soft-line);
  border-radius: 8px;
  padding: 14px;
}
.summary span {
  color: var(--workflow-muted);
  display: block;
  font-size: 0.82em;
  margin-bottom: 4px;
}
.summary strong {
  font-size: 1.1em;
}
.export-panel {
  align-items: center;
  display: flex;
  gap: 20px;
  justify-content: space-between;
  margin-bottom: 18px;
}
.export-panel h2 {
  font-size: 1.05em;
  margin-bottom: 4px;
}
.export-panel p {
  color: var(--workflow-muted);
  font-size: 0.92em;
}
.export-panel .eyebrow {
  color: var(--workflow-eyebrow);
}
.export-actions {
  display: flex;
  gap: 10px;
}
.section-head {
  align-items: center;
  display: flex;
  gap: 16px;
  justify-content: space-between;
  margin-bottom: 14px;
}
table {
  border-collapse: collapse;
  width: 100%;
}
th,
td {
  border-bottom: 1px solid var(--workflow-soft-line);
  padding: 10px 8px;
  text-align: left;
  vertical-align: top;
}
th {
  color: var(--workflow-muted);
  font-size: 0.78em;
  text-transform: uppercase;
}
td span {
  color: var(--workflow-muted);
  display: block;
  font-size: 0.85em;
}
tbody tr:hover {
  background: rgba(148, 163, 184, 0.05);
}
tr.selected td {
  background: rgba(59, 130, 246, 0.08);
}
.confidence {
  border-radius: 999px;
  display: inline-flex;
  padding: 3px 8px;
}
.confidence.high {
  background: rgba(34, 197, 94, 0.14);
  color: #86efac;
}
.confidence.medium {
  background: rgba(250, 204, 21, 0.14);
  color: #fde68a;
}
.confidence.low {
  background: rgba(248, 113, 113, 0.14);
  color: #fca5a5;
}
.confidence.unknown {
  background: rgba(148, 163, 184, 0.08);
  color: var(--workflow-muted);
}
.check-pill {
  border-radius: 999px;
  display: inline-flex;
  font-size: 0.82em;
  padding: 3px 8px;
  width: fit-content;
}
.check-pill.ok {
  background: rgba(34, 197, 94, 0.14);
  color: #86efac;
}
.check-pill.warning {
  background: rgba(250, 204, 21, 0.14);
  color: #fde68a;
}
.check-pill.neutral {
  background: rgba(148, 163, 184, 0.08);
  color: var(--workflow-muted);
}
.check-message {
  color: #fde68a;
  display: block;
  font-size: 0.86em;
  margin-top: 6px;
}
.empty {
  color: var(--workflow-muted);
  padding: 18px 0;
}
.error {
  color: #fca5a5;
  margin-bottom: 18px;
}
.detail-overlay {
  align-items: center;
  background: rgba(10, 12, 17, 0.76);
  display: flex;
  inset: 0;
  justify-content: center;
  padding: 24px;
  position: fixed;
  z-index: 30;
}
.detail-panel {
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  height: min(860px, calc(100vh - 48px));
  max-height: min(860px, calc(100vh - 48px));
  max-width: min(1360px, calc(100vw - 48px));
  overflow: hidden;
  width: 100%;
}
.detail-head {
  align-items: flex-start;
  display: flex;
  gap: 16px;
  justify-content: space-between;
  margin-bottom: 16px;
}
.detail-head h2 {
  font-size: 1.2em;
  margin-bottom: 4px;
}
.detail-head p:not(.eyebrow) {
  color: var(--workflow-muted);
}
.detail-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: minmax(520px, 1.35fr) minmax(360px, 0.9fr);
  min-height: 0;
}
.document-preview {
  background: var(--workflow-input);
  border: 1px solid var(--workflow-soft-line);
  border-radius: 8px;
  align-content: start;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  min-height: 0;
  overflow: hidden;
  padding: 12px;
}
.preview-toolbar {
  align-items: center;
  border-bottom: 1px solid var(--workflow-line);
  display: flex;
  gap: 10px;
  margin: -12px -12px 12px;
  padding: 10px 12px;
}
.preview-toolbar span {
  color: var(--workflow-text);
  font-weight: 600;
  min-width: 48px;
  text-align: center;
}
.preview-toolbar .page-count {
  min-width: 88px;
}
.preview-canvas {
  align-items: start;
  display: grid;
  height: 100%;
  justify-items: center;
  min-height: 0;
  overflow: auto;
  overscroll-behavior: contain;
  scrollbar-width: none;
}
.preview-canvas::-webkit-scrollbar {
  display: none;
}
.document-preview img {
  border-radius: 6px;
  align-self: start;
  height: auto;
  max-width: none;
  object-fit: contain;
  transition: width 0.12s ease;
}
.pdf-placeholder {
  border: 1px dashed var(--workflow-line);
  border-radius: 8px;
  color: var(--workflow-muted);
  padding: 24px;
}
.pdf-placeholder h3 {
  color: var(--workflow-text);
  margin-bottom: 6px;
}
.detail-content {
  display: grid;
  gap: 18px;
  min-height: 0;
  overflow: auto;
  overscroll-behavior: contain;
  padding-right: 4px;
}
.field-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}
.field-grid div {
  background: var(--workflow-input);
  border: 1px solid var(--workflow-soft-line);
  border-radius: 8px;
  padding: 12px;
}
dt {
  color: var(--workflow-muted);
  font-size: 0.76em;
  margin-bottom: 4px;
  text-transform: uppercase;
}
dd {
  color: var(--workflow-text);
}
.line-items,
.audit-log,
.raw-text {
  background: var(--workflow-input);
  border: 1px solid var(--workflow-soft-line);
  border-radius: 8px;
  padding: 14px;
}
.line-items h3,
.audit-log h3,
.raw-text h3 {
  font-size: 1em;
  margin-bottom: 10px;
}
.audit-log td {
  overflow-wrap: anywhere;
}
.raw-text textarea {
  background: var(--workflow-panel);
  border: 1px solid var(--workflow-line);
  border-radius: 8px;
  color: var(--workflow-text);
  font: inherit;
  line-height: 1.5;
  padding: 12px;
  resize: vertical;
  width: 100%;
}
@media (max-width: 760px) {
  header,
  .section-head,
  .export-panel,
  .detail-head {
    align-items: flex-start;
    flex-direction: column;
  }
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .detail-overlay {
    align-items: stretch;
    padding: 12px;
  }
  .detail-panel {
    height: calc(100vh - 24px);
    max-height: calc(100vh - 24px);
    max-width: calc(100vw - 24px);
  }
  .document-preview {
    min-height: 52vh;
  }
  .export-actions {
    width: 100%;
  }
  .export-actions select,
  .export-actions button {
    flex: 1;
  }
  table {
    display: block;
    overflow-x: auto;
  }
}
</style>
