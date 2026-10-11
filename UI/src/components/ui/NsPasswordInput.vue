<script setup lang="ts">
import Control from "primevue/password"
defineOptions({ inheritAttrs: false })
</script>

<template>
  <Control class="ns-password" v-bind="$attrs">
    <template v-for="(_, name) in $slots" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}" />
    </template>
  </Control>
</template>
