<script setup lang="ts">
import Control from "primevue/inputnumber"
defineOptions({ inheritAttrs: false })
</script>

<template>
  <Control class="ns-inputnumber" v-bind="$attrs">
    <template v-for="(_, name) in $slots" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps || {}" />
    </template>
  </Control>
</template>
