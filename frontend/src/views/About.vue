<template>
  <div class="container about">
    <header>
      <h1>About Phlow</h1>
      <p class="lead">
        Phlow is bookkeeping infrastructure for Filipino accounting firms: intake, extraction,
        review, reconciliation, and compliance support in one focused workspace.
      </p>
    </header>

    <section>
      <h2>Why we exist</h2>
      <p>
        Global accounting tools were built for North American CPAs. They don't speak BIR,
        can't read handwritten palengke receipts, and price in dollars for firms that bill
        in pesos. Filipino bookkeepers end up doing by hand what software should be doing
        for them.
      </p>
      <p>
        Phlow builds the missing layer: opinionated, locally-aware tools that fit the
        way work actually happens here.
      </p>
    </section>

    <section>
      <h2>How we build</h2>
      <ul>
        <li><strong>One workflow at a time.</strong> New capabilities ship when they make the core bookkeeping flow faster.</li>
        <li><strong>Local by design.</strong> Built for PH workflows, BIR formats, and PH banking statements first &mdash; not as an afterthought.</li>
        <li><strong>Sell the result, not the plumbing.</strong> Customers get hours back; the API is for power users underneath.</li>
        <li><strong>Opinionated defaults.</strong> Sensible behavior out of the box; few knobs to fiddle with.</li>
      </ul>
    </section>

    <section>
      <h2>Founder</h2>
      <p>
        [Your name here] &mdash; [short bio: where you're based, what you did before, why
        you're building this]. Edit <code>src/views/About.vue</code> to put your real bio in.
      </p>
    </section>

    <section>
      <h2>Stack we use</h2>
      <ul>
        <li><strong>Python + FastAPI</strong> for backend APIs.</li>
        <li><strong>Vue 3 + Vite</strong> for the product UI and marketing pages.</li>
        <li><strong>PostgreSQL</strong> for persistence.</li>
        <li><strong>OpenAI</strong> and other models, called from our backend &mdash; never from the browser.</li>
      </ul>
    </section>

    <section>
      <h2>Get in touch</h2>
      <p>
        Are you a Filipino bookkeeper, accountant, or SMB owner with a back-office headache?
        We work with a small group of design partners before public release.
      </p>
      <p>
        <a href="mailto:hello@phlow.app">hello@phlow.app</a>
        &middot;
        <a href="https://github.com/yourname" target="_blank" rel="noopener">GitHub</a>
      </p>
    </section>
  </div>
</template>

<style scoped>
.about {
  max-width: 720px;
  padding: 0 24px;
}
header {
  margin-bottom: 40px;
}
header h1 {
  margin-bottom: 12px;
}
.lead {
  color: var(--muted);
  font-size: 1.1em;
}
section {
  margin-bottom: 36px;
}
section h2 {
  margin-bottom: 12px;
  font-size: 1.25em;
}
section p {
  margin-bottom: 12px;
}
section ul {
  margin-left: 24px;
}
section li {
  margin-bottom: 8px;
}
code {
  background: var(--surface-2);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
}
</style>
