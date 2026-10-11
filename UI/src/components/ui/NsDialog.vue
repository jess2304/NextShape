<script setup lang="ts">
import Control from "primevue/dialog"
defineOptions({ inheritAttrs: false })
</script>

<template>
  <Control modal :draggable="false" class="ns-dialog" v-bind="$attrs">
    <template v-for="(_, name) in $slots" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}" />
    </template>
  </Control>
</template>
