<template>
  <div class="container docs">
    <aside>
      <h4>Reference</h4>
      <ul>
        <li><a href="#auth">Authentication</a></li>
        <li><a href="#extract">POST /v1/extract-receipt</a></li>
        <li><a href="#response">Response shape</a></li>
        <li><a href="#errors">Errors</a></li>
        <li><a href="#limits">Limits</a></li>
      </ul>
    </aside>

    <article>
      <h1>PhlowBooks API</h1>
      <p class="lead">
        For developer-savvy firms who want to call PhlowBooks directly. Most users start with the
        <router-link to="/phlowbooks">web app</router-link> instead.
      </p>
      <p class="lead">
        Base URL: <code>https://api.phlowbooks.app</code>
      </p>

      <h2 id="auth">Authentication</h2>
      <p>All requests require an API key sent in the <code>x-api-key</code> header.</p>
      <pre><code>x-api-key: your-key-here</code></pre>
      <p class="muted-note">
        During v0 there is a single shared API key set by the server operator.
        Per-user keys arrive when user accounts ship.
      </p>

      <h2 id="extract">POST /v1/extract-receipt</h2>
      <p>Upload a receipt, invoice, GCash, Maya, or bank screenshot image. Returns the raw OCR text plus structured fields tuned for Philippine bookkeeping.</p>

      <h3>Request</h3>
      <p>Multipart form upload with one file field named <code>file</code>.</p>
      <ul>
        <li>Accepted types: <code>image/jpeg</code>, <code>image/png</code>, <code>image/webp</code></li>
        <li>Max size: 20 MB (configurable)</li>
        <li>Header: <code>x-api-key: your-key</code></li>
      </ul>

      <h3>cURL</h3>
      <pre><code>curl -X POST https://api.phlowbooks.app/v1/extract-receipt \
  -H "x-api-key: your-key" \
  -F "file=@receipt.jpg"</code></pre>

      <h3>JavaScript (fetch)</h3>
      <pre><code>const fd = new FormData()
fd.append('file', fileInput.files[0])

const res = await fetch('https://api.phlowbooks.app/v1/extract-receipt', {
  method: 'POST',
  headers: { 'x-api-key': 'your-key' },
  body: fd,
})
const json = await res.json()</code></pre>

      <h3>Python (requests)</h3>
      <pre><code>import requests

with open('receipt.jpg', 'rb') as f:
    res = requests.post(
        'https://api.phlowbooks.app/v1/extract-receipt',
        headers={'x-api-key': 'your-key'},
        files={'file': f},
    )
print(res.json())</code></pre>

      <h2 id="response">Response shape</h2>
      <p>Status <code>200</code> on success.</p>
      <pre><code>{
  "raw_text": "string  // full OCR output",
  "data": {
    "vendor":          "string | null",
    "vendor_tin":      "string | null",
    "or_number":       "string | null",
    "si_number":       "string | null",
    "date":            "YYYY-MM-DD | null",
    "currency":        "PHP",
    "subtotal":        "number | null",
    "tax":             "number | null",
    "vat_type":        "vatable | zero_rated | exempt | non_vat | null",
    "vatable_amount":  "number | null",
    "vat_amount":      "number | null",
    "total":           "number | null",
    "doc_type":        "official_receipt | sales_invoice | gcash | maya | bank_statement | other | null",
    "confidence":      "number | null",
    "line_items": [
      {
        "description": "string",
        "quantity":    "number | null",
        "unit_price":  "number | null",
        "total":       "number | null"
      }
    ]
  }
}</code></pre>

      <h2 id="errors">Errors</h2>
      <table>
        <thead>
          <tr><th>Status</th><th>Meaning</th></tr>
        </thead>
        <tbody>
          <tr><td>400</td><td>Unsupported file type</td></tr>
          <tr><td>401</td><td>Missing or invalid API key</td></tr>
          <tr><td>413</td><td>File exceeds size limit</td></tr>
          <tr><td>422</td><td>Missing <code>file</code> field</td></tr>
          <tr><td>500</td><td>OCR or extraction error</td></tr>
        </tbody>
      </table>

      <h2 id="limits">Limits</h2>
      <ul>
        <li>Max file size: 20 MB.</li>
        <li>Synchronous response &mdash; typical latency 5&ndash;15 seconds per image.</li>
        <li>No rate limits in v0; polite use only.</li>
      </ul>
    </article>
  </div>
</template>

<style scoped>
.docs {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 48px;
  align-items: start;
}
aside {
  position: sticky;
  top: 88px;
}
aside h4 {
  margin-bottom: 12px;
  color: var(--muted);
  text-transform: uppercase;
  font-size: 0.75em;
  letter-spacing: 0.08em;
}
aside ul {
  list-style: none;
}
aside li {
  margin-bottom: 8px;
}
aside a {
  color: var(--text);
  font-size: 0.92em;
}
aside a:hover {
  color: var(--accent);
}

article h1 {
  margin-bottom: 8px;
}
article h2 {
  margin: 40px 0 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}
article h3 {
  margin: 22px 0 10px;
  font-size: 1em;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
article p {
  margin-bottom: 12px;
}
article ul {
  margin: 12px 0 16px 24px;
}
article li {
  margin-bottom: 6px;
}
article pre {
  background: var(--code-bg);
  padding: 16px 20px;
  border-radius: 10px;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid var(--border);
  font-size: 0.88em;
}
article code {
  background: var(--surface-2);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
article pre code {
  background: none;
  padding: 0;
}
article table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}
article th,
article td {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
}
article th {
  color: var(--muted);
  font-weight: 500;
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.lead {
  color: var(--muted);
  margin-bottom: 32px;
}
.muted-note {
  color: var(--muted);
  font-size: 0.9em;
}

@media (max-width: 768px) {
  .docs {
    grid-template-columns: 1fr;
  }
  aside {
    position: static;
  }
}
</style>
