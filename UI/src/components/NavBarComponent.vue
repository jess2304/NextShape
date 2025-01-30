<script setup lang="ts">
import Menubar from "primevue/menubar"
import Button from "primevue/button"
</script>
<template>
  <Menubar :model="[]" class="p-0">
    <template #start>
      <div class="flex align-items-center">
        <img src="/nextshape.png" alt="Next Shape Icon" class="w-1" />
        <Button text label="Next Shape" class="text-4xl no-hover p-0" /></div
    ></template>
  </Menubar>
</template>
<style>
.no-hover:hover {
  background-color: inherit !important;
}
</style>
