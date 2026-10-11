<script setup lang="ts">
import Control from "primevue/button"
defineOptions({ inheritAttrs: false })
</script>

<template>
  <Control type="button" class="ns-button" v-bind="$attrs">
    <template v-for="(_, name) in $slots" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}" />
    </template>
  </Control>
</template>
