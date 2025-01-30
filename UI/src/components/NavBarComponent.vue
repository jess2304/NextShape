<script setup lang="ts">
import Menubar from "primevue/menubar"
import Button from "primevue/button"
</script>
<template>
  <Menubar :model="[]" class="p-0">
    <template #start>
      <Button text label="Next Shape" class="text-4xl no-hover" />
    </template>
  </Menubar>
</template>
<style>
.no-hover:hover {
  background-color: inherit !important;
}
</style>
