<script setup lang="ts">
defineProps<{ eyebrow?: string; title: string; description?: string }>()
</script>

<template>
  <header class="page-header">
    <div class="page-header__copy">
      <p v-if="eyebrow" class="ns-eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p v-if="description" class="page-header__description">
        {{ description }}
      </p>
    </div>
    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.page-header__copy {
  max-width: 47rem;
}
.page-header h1 {
  font-size: clamp(1.65rem, 3vw, 2.25rem);
  letter-spacing: -0.045em;
  line-height: 1.18;
  margin: 0;
  font-weight: 600;
}
.page-header__description {
  color: var(--ns-muted);
  margin: 0.8rem 0 0;
  font-size: 0.95rem;
  line-height: 1.7;
}
.page-header__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  flex-shrink: 0;
}
@media (max-width: 640px) {
  .page-header {
    align-items: start;
    flex-direction: column;
    margin-bottom: 1.5rem;
    gap: 1rem;
  }
}
</style>
