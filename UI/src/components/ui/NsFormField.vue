<script setup lang="ts">
defineProps<{
  id: string
  label: string
  hint?: string
  error?: string
  required?: boolean
}>()
</script>

<template>
  <div class="ns-field">
    <label :for="id" class="ns-field__label"
      >{{ label }}<span v-if="required" aria-hidden="true"> *</span></label
    >
    <slot
      :describedby="error ? `${id}-error` : hint ? `${id}-hint` : undefined"
    />
    <small
      v-if="error"
      :id="`${id}-error`"
      class="ns-field__error"
      role="alert"
      >{{ error }}</small
    >
    <small v-else-if="hint" :id="`${id}-hint`" class="ns-field__hint">{{
      hint
    }}</small>
  </div>
</template>

<style scoped>
.ns-field {
  display: grid;
  gap: 0.5rem;
  min-width: 0;
  align-content: start;
}
.ns-field__label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ns-ink);
}
.ns-field__label span,
.ns-field__error {
  color: var(--ns-danger);
}
.ns-field__hint {
  color: var(--ns-muted);
}
.ns-field__hint,
.ns-field__error {
  font-size: 0.8rem;
  line-height: 1.5;
}
.ns-field :deep(.p-inputtext),
.ns-field :deep(.p-inputnumber),
.ns-field :deep(.p-password),
.ns-field :deep(.p-select),
.ns-field :deep(.p-multiselect),
.ns-field :deep(.p-datepicker),
.ns-field :deep(.p-textarea) {
  width: 100%;
  min-width: 0;
}
</style>
