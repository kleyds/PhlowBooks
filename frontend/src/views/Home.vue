<template>
  <div>
    <section class="hero">
      <div class="container">
        <span class="badge">PhlowBooks &middot; bookkeeping infrastructure for PH firms</span>
        <h1>Receipts in.<br />Clean entries out.</h1>
        <p class="lead">
          PhlowBooks turns receipts, invoices, wallet screenshots, and bank documents into clean
          accounting entries for Filipino bookkeepers and accounting firms.
        </p>
        <div class="cta">
          <router-link to="/phlowbooks" class="btn">Explore PhlowBooks</router-link>
          <router-link to="/about" class="btn secondary">About us</router-link>
        </div>
      </div>
    </section>

    <section class="container values">
      <div class="value">
        <h3>Built for PH, not adapted</h3>
        <p>BIR forms, OR/SI/TIN parsing, GCash and Maya statements, Tagalog OCR &mdash; first-class, not bolted on.</p>
      </div>
      <div class="value">
        <h3>Priced in pesos</h3>
        <p>Pricing tiers that fit a Filipino solo bookkeeper or a 10-seat accounting firm. No USD enterprise tax.</p>
      </div>
      <div class="value">
        <h3>One job, done well</h3>
        <p>Each tool solves a single, narrow problem in your back office &mdash; not a sprawling platform.</p>
      </div>
    </section>

    <section class="container products-preview">
      <div class="section-head">
        <h2>Platform</h2>
        <router-link to="/products" class="see-all">See the workflow &rarr;</router-link>
      </div>
      <div class="grid">
        <router-link to="/phlowbooks" class="product-card">
          <div class="product-icon">₱</div>
          <h3>PhlowBooks</h3>
          <p>Bookkeeping infrastructure for Filipino accounting firms. Receipts in, clean entries out.</p>
          <span class="status live">Private beta</span>
        </router-link>
        <router-link to="/docs" class="product-card">
          <div class="product-icon muted">API</div>
          <h3>Developer access</h3>
          <p>Power-user firms can connect directly to the extraction API when they need deeper workflow control.</p>
          <span class="status soon">Docs</span>
        </router-link>
      </div>
    </section>

    <section class="container cta-band">
      <div class="cta-inner">
        <h2>Like the approach?</h2>
        <p>We work with a small number of design partners before public release.</p>
        <router-link to="/about" class="btn">Get in touch</router-link>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  padding: 96px 0 64px;
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
  font-size: clamp(2.2em, 5vw, 3.4em);
  margin-bottom: 20px;
  background: linear-gradient(120deg, #e7e9ee 0%, #818cf8 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.lead {
  font-size: 1.15em;
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
}

.values {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
  padding: 64px 24px;
}
.value h3 {
  margin-bottom: 8px;
  font-size: 1.05em;
}
.value p {
  color: var(--muted);
  font-size: 0.95em;
}

.products-preview {
  padding: 32px 24px 64px;
}
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}
.see-all {
  color: var(--muted);
  font-size: 0.95em;
}
.see-all:hover {
  color: var(--accent);
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}
.product-card {
  display: block;
  background: var(--surface);
  padding: 28px;
  border-radius: 12px;
  border: 1px solid var(--border);
  color: var(--text);
  position: relative;
  transition: border-color 0.15s ease, transform 0.15s ease;
}
.product-card:hover:not(.disabled) {
  border-color: var(--accent);
  transform: translateY(-2px);
  color: var(--text);
}
.product-card.disabled {
  opacity: 0.7;
  cursor: default;
}
.product-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: var(--accent);
  color: white;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  margin-bottom: 16px;
}
.product-icon.muted {
  background: var(--surface-2);
  color: var(--muted);
}
.product-card h3 {
  margin-bottom: 8px;
  font-size: 1.1em;
}
.product-card p {
  color: var(--muted);
  font-size: 0.95em;
}
.status {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 0.75em;
  padding: 3px 10px;
  border-radius: 999px;
  letter-spacing: 0.04em;
}
.status.live {
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-hover);
}
.status.soon {
  background: var(--surface-2);
  color: var(--muted);
}

.cta-band {
  padding: 64px 24px 32px;
}
.cta-inner {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 48px 32px;
  text-align: center;
}
.cta-inner h2 {
  margin-bottom: 8px;
}
.cta-inner p {
  color: var(--muted);
  margin-bottom: 24px;
}
</style>
