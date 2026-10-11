<script setup lang="ts">
withDefaults(
  defineProps<{ title: string; description?: string; icon?: string }>(),
  { icon: "pi pi-inbox" }
)
</script>

<template>
  <div class="ns-empty">
    <span class="ns-empty__icon" :class="icon" aria-hidden="true" />
    <h2>{{ title }}</h2>
    <p v-if="description">{{ description }}</p>
    <div v-if="$slots.default" class="ns-empty__actions"><slot /></div>
  </div>
</template>

<style scoped>
.ns-empty {
  display: grid;
  justify-items: center;
  text-align: center;
  padding: clamp(2rem, 5vw, 4rem) 1rem;
}
.ns-empty__icon {
  display: grid;
  place-items: center;
  width: 3.5rem;
  height: 3.5rem;
  margin-bottom: 1.25rem;
  border-radius: 50%;
  background: var(--ns-sage);
  color: var(--ns-primary);
  font-size: 1.25rem;
}
.ns-empty h2 {
  font-size: 1.125rem;
  margin: 0;
}
.ns-empty p {
  max-width: 29rem;
  color: var(--ns-muted);
  font-size: 0.925rem;
  margin: 0.75rem 0 0;
}
.ns-empty__actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
</style>
