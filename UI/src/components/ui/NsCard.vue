<template>
  <section class="ns-card">
    <header v-if="$slots.header" class="ns-card__header">
      <slot name="header" />
    </header>
    <slot />
    <footer v-if="$slots.footer" class="ns-card__footer">
      <slot name="footer" />
    </footer>
  </section>
</template>

<style scoped>
.ns-card {
  min-width: 0;
  padding: clamp(1.25rem, 3vw, 2rem);
  background: var(--ns-surface);
  border: 1px solid var(--ns-border);
  border-radius: var(--ns-radius);
  box-shadow: var(--ns-shadow);
}
.ns-card__header {
  margin-bottom: 1.5rem;
}
.ns-card__footer {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--ns-border);
}
</style>
