<template>
  <div>
    <section class="hero">
      <div class="container">
        <span class="badge">Pre-MVP &middot; Built for Philippine firms</span>
        <h1>Stop typing resibos.</h1>
        <p class="lead">
          Phlow turns receipts, invoices, wallet screenshots, and bank documents into
          clean accounting entries for Filipino bookkeepers who are tired of typing by hand.
        </p>
        <div class="cta">
          <a href="#waitlist" class="btn">Join the waitlist</a>
          <a href="#how" class="btn secondary">How it works</a>
        </div>
      </div>
    </section>

    <section class="container problem">
      <h2>The problem</h2>
      <div class="problem-grid">
        <div>
          <h3>Hours per week, gone</h3>
          <p>The average bookkeeper retypes hundreds of receipts a week. That's billable time you can't bill.</p>
        </div>
        <div>
          <h3>Global tools don't speak BIR</h3>
          <p>Hubdoc and Dext skip TIN, OR/SI, ATP fields. Textract chokes on handwritten palengke receipts.</p>
        </div>
        <div>
          <h3>GCash, Maya, BPI, BDO &mdash; every format different</h3>
          <p>Five banks, five PDF layouts. You parse them by hand or you don't reconcile at all.</p>
        </div>
        <div>
          <h3>Clients send chaos</h3>
          <p>Phone photos in Viber, screenshots in Messenger, scanned PDFs over email. Nothing's tidy.</p>
        </div>
      </div>
    </section>

    <section id="how" class="container how">
      <h2>How it works</h2>
      <ol class="steps">
        <li>
          <span class="step-num">1</span>
          <div>
            <h3>Receipts come in</h3>
            <p>Select a client, then upload receipt photos in batches of up to 50 files.</p>
          </div>
        </li>
        <li>
          <span class="step-num">2</span>
          <div>
            <h3>Phlow reads them</h3>
            <p>Vendor name, TIN, OR/SI number, date, VAT type, vatable amount, VAT, total, and document type are extracted for review.</p>
          </div>
        </li>
        <li>
          <span class="step-num">3</span>
          <div>
            <h3>You review and approve</h3>
            <p>Side-by-side original document and editable fields. Fix low-confidence values before they reach your books.</p>
          </div>
        </li>
        <li>
          <span class="step-num">4</span>
          <div>
            <h3>Export clean CSVs</h3>
            <p>Export approved receipts in QuickBooks Online, Xero, or generic CSV formats. Your accounting software stays the system of record.</p>
          </div>
        </li>
      </ol>
    </section>

    <section class="container why">
      <h2>Why Phlow (and not Hubdoc, Dext, or Textract)</h2>
      <div class="compare">
        <div class="compare-row head">
          <div></div>
          <div>Phlow</div>
          <div>Global tools</div>
        </div>
        <div class="compare-row">
          <div>Handwritten Filipino receipts</div>
          <div class="yes">Built for them</div>
          <div class="no">Often unreadable</div>
        </div>
        <div class="compare-row">
          <div>BIR OR format (TIN, ATP, OR/SI #)</div>
          <div class="yes">First-class fields</div>
          <div class="no">Not parsed</div>
        </div>
        <div class="compare-row">
          <div>GCash, Maya, BPI, BDO documents</div>
          <div class="yes">PH document types</div>
          <div class="no">Manual mapping</div>
        </div>
        <div class="compare-row">
          <div>Review workflow for noisy OCR</div>
          <div class="yes">Human-in-the-loop</div>
          <div class="no">Opaque automation</div>
        </div>
        <div class="compare-row">
          <div>Pricing in pesos</div>
          <div class="yes">Designed for PH firm sizes</div>
          <div class="no">USD, enterprise tiers</div>
        </div>
        <div class="compare-row">
          <div>Free seats for your SMB clients</div>
          <div class="yes">Yes &mdash; you pay, they upload</div>
          <div class="no">Per-seat pricing for everyone</div>
        </div>
      </div>
    </section>

    <section class="container built-for">
      <h2>Built for bookkeepers</h2>
      <div class="features-grid">
        <div class="feature">
          <h3>Multi-client workspace</h3>
          <p>Manage all your clients in one workspace. Switch between books in two clicks.</p>
        </div>
        <div class="feature">
          <h3>Client-scoped records</h3>
          <p>Receipts, documents, review queues, and exports stay attached to the right business.</p>
        </div>
        <div class="feature">
          <h3>Bulk processing</h3>
          <p>Upload up to 50 files at once and let extraction run in the background.</p>
        </div>
        <div class="feature">
          <h3>PH-tuned extraction</h3>
          <p>First-class fields for vendor TIN, OR/SI numbers, VAT type, vatable amount, and VAT amount.</p>
        </div>
        <div class="feature">
          <h3>Review queue</h3>
          <p>Approve or reject extracted receipts from a focused two-panel workspace.</p>
        </div>
        <div class="feature">
          <h3>API access</h3>
          <p>Power-user firms can hit our HTTP API directly. <router-link to="/docs">See the docs</router-link>.</p>
        </div>
      </div>
    </section>

    <section class="container scope">
      <h2>MVP scope</h2>
      <div class="scope-grid">
        <div>
          <span>01</span>
          <h3>Bookkeeper auth</h3>
          <p>Email/password accounts with JWT sessions.</p>
        </div>
        <div>
          <span>02</span>
          <h3>Multi-client workspace</h3>
          <p>One firm account, many client businesses.</p>
        </div>
        <div>
          <span>03</span>
          <h3>Batch receipt upload</h3>
          <p>Client-scoped uploads with extraction queued behind the scenes.</p>
        </div>
        <div>
          <span>04</span>
          <h3>PH receipt extraction</h3>
          <p>BIR and VAT fields, document type detection, and confidence scoring.</p>
        </div>
        <div>
          <span>05</span>
          <h3>Review queue</h3>
          <p>Editable fields beside the original image.</p>
        </div>
        <div>
          <span>06</span>
          <h3>CSV export</h3>
          <p>QuickBooks Online, Xero, and generic formats.</p>
        </div>
        <div>
          <span>07</span>
          <h3>Receipt archive</h3>
          <p>Search and filter approved receipts per client.</p>
        </div>
        <div>
          <span>08</span>
          <h3>Billing</h3>
          <p>Paymongo subscriptions with plan-based receipt limits.</p>
        </div>
      </div>
    </section>

    <section class="container pricing">
      <h2>Pricing to validate</h2>
      <div class="pricing-table">
        <div class="pricing-row head">
          <div>Tier</div>
          <div>Price</div>
          <div>Receipts/mo</div>
          <div>Users</div>
        </div>
        <div class="pricing-row">
          <div>Solo</div>
          <div>PHP 1,500</div>
          <div>500</div>
          <div>1</div>
        </div>
        <div class="pricing-row">
          <div>Firm</div>
          <div>PHP 5,000</div>
          <div>2,000</div>
          <div>5</div>
        </div>
        <div class="pricing-row">
          <div>Agency</div>
          <div>PHP 12,000</div>
          <div>10,000</div>
          <div>Unlimited</div>
        </div>
      </div>
    </section>

    <section id="waitlist" class="container waitlist">
      <div class="waitlist-inner">
        <h2>Join the private beta</h2>
        <p>
          We're working with a small group of Filipino bookkeepers and accounting firms before
          public release. Early access gets locked-in launch pricing and a direct line to the founder.
        </p>
        <form @submit.prevent="onSubmit" class="form">
          <input
            v-model="email"
            type="email"
            required
            placeholder="you@yourfirm.ph"
            aria-label="Your email"
          />
          <button type="submit" class="btn">Request access</button>
        </form>
        <p v-if="submitted" class="success">
          Thanks! We'll be in touch within a week.
        </p>
        <p class="hint">
          Or email <a href="mailto:hello@phlow.app">hello@phlow.app</a> directly.
        </p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const email = ref('')
const submitted = ref(false)

function onSubmit() {
  // TODO wire to backend waitlist endpoint
  submitted.value = true
  email.value = ''
}
</script>

<style scoped>
.hero {
  padding: 96px 0 72px;
  text-align: center;
  background:
    radial-gradient(circle at 20% 0%, rgba(99, 102, 241, 0.18), transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(129, 140, 248, 0.12), transparent 50%);
  border-bottom: 1px solid var(--border);
}
.badge {
  display: inline-block;
  padding: 4px 12px;
  background: var(--surface-2);
  color: var(--muted);
  border-radius: 999px;
  font-size: 0.8em;
  margin-bottom: 24px;
  letter-spacing: 0.02em;
}
.hero h1 {
  font-size: clamp(2.4em, 5.5vw, 3.6em);
  margin-bottom: 20px;
  background: linear-gradient(120deg, #e7e9ee 0%, #818cf8 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.lead {
  font-size: 1.18em;
  color: var(--muted);
  max-width: 680px;
  margin: 0 auto 32px;
}
.cta {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
.btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 8px;
  background: var(--accent);
  color: white;
  font-weight: 500;
  border: none;
  cursor: pointer;
  font-size: 1em;
  transition: background 0.15s ease;
}
.btn:hover {
  background: var(--accent-hover);
  color: white;
}
.btn.secondary {
  background: var(--surface-2);
  color: var(--text);
}
.btn.secondary:hover {
  background: var(--border);
  color: var(--text);
}

section {
  padding: 64px 24px;
}
section h2 {
  font-size: 1.6em;
  margin-bottom: 28px;
  text-align: center;
}

.problem-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}
.problem-grid h3 {
  margin-bottom: 8px;
  font-size: 1.05em;
}
.problem-grid p {
  color: var(--muted);
  font-size: 0.95em;
}

.steps {
  list-style: none;
  max-width: 720px;
  margin: 0 auto;
  padding: 0;
}
.steps li {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
  align-items: flex-start;
}
.step-num {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--accent);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}
.steps h3 {
  margin-bottom: 4px;
  font-size: 1.05em;
}
.steps p {
  color: var(--muted);
  font-size: 0.95em;
}

.compare {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  max-width: 860px;
  margin: 0 auto;
}
.compare-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  font-size: 0.95em;
  align-items: center;
}
.compare-row:last-child {
  border-bottom: none;
}
.compare-row.head {
  background: var(--surface-2);
  color: var(--muted);
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}
.compare-row .yes {
  color: var(--accent-hover);
}
.compare-row .no {
  color: var(--muted);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}
.feature {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
}
.feature h3 {
  margin-bottom: 8px;
  font-size: 1.05em;
}
.feature p {
  color: var(--muted);
  font-size: 0.95em;
}

.scope-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 16px;
}
.scope-grid > div {
  border-top: 1px solid var(--border);
  padding-top: 18px;
}
.scope-grid span {
  display: block;
  color: var(--accent-hover);
  font-size: 0.78em;
  margin-bottom: 8px;
  font-weight: 700;
}
.scope-grid h3 {
  margin-bottom: 6px;
  font-size: 1em;
}
.scope-grid p {
  color: var(--muted);
  font-size: 0.93em;
}

.pricing-table {
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  max-width: 860px;
  margin: 0 auto;
}
.pricing-row {
  display: grid;
  grid-template-columns: 1.1fr 1fr 1fr 1fr;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border);
  font-size: 0.95em;
}
.pricing-row:last-child {
  border-bottom: none;
}
.pricing-row.head {
  background: var(--surface-2);
  color: var(--muted);
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 500;
}

.waitlist-inner {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 48px 32px;
  text-align: center;
  max-width: 640px;
  margin: 0 auto;
}
.waitlist-inner h2 {
  margin-bottom: 12px;
}
.waitlist-inner p {
  color: var(--muted);
  margin-bottom: 24px;
}
.form {
  display: flex;
  gap: 8px;
  max-width: 480px;
  margin: 0 auto;
  flex-wrap: wrap;
  justify-content: center;
}
.form input {
  flex: 1;
  min-width: 220px;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font-size: 1em;
}
.form input:focus {
  outline: none;
  border-color: var(--accent);
}
.success {
  margin-top: 16px;
  color: var(--accent-hover);
  font-size: 0.95em;
}
.hint {
  margin-top: 20px;
  font-size: 0.9em;
  color: var(--muted);
}

@media (max-width: 640px) {
  .compare-row,
  .pricing-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
  .compare-row.head,
  .pricing-row.head {
    display: none;
  }
}
</style>
