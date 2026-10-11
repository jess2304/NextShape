<script setup lang="ts">
withDefaults(
  defineProps<{ tone?: "neutral" | "success" | "warning" | "danger" }>(),
  { tone: "neutral" }
)
</script>

<template>
  <span class="ns-badge" :class="`ns-badge--${tone}`"><slot /></span>
</template>

<style scoped>
.ns-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.3rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  line-height: 1.4;
  font-weight: 600;
  background: var(--ns-sage);
  color: var(--ns-primary);
}
.ns-badge--success {
  background: #e7f2e9;
  color: #285b34;
}
.ns-badge--warning {
  background: #faf0db;
  color: #77511d;
}
.ns-badge--danger {
  background: #faeae6;
  color: #983d2c;
}
</style>
