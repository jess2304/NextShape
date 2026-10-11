<script setup lang="ts">
import Control from "primevue/inputotp"
defineOptions({ inheritAttrs: false })
</script>

<template>
  <Control class="ns-inputotp" v-bind="$attrs">
    <template v-for="(_, name) in $slots" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}" />
    </template>
  </Control>
</template>
