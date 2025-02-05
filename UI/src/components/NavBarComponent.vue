<script setup lang="ts">
import Menubar from "primevue/menubar"
import Button from "primevue/button"
import { NAVBAR_ELEMENTS } from "@/assets/js/constants"
</script>
<template>
  <Menubar :model="NAVBAR_ELEMENTS">
    <template #start>
      <img
        src="/nextshape.png"
        alt="Next Shape Icon"
        class="w-1 flex-shrink-0" />
      <Button text label="Next Shape" class="text-4xl no-hover p-0"
    /></template>
    <template #item="{ item, props, hasSubmenu }">
      <router-link
        v-if="item.route"
        v-slot="{ href, navigate }"
        :to="item.route"
        custom
      >
        <a v-ripple :href="href" v-bind="props.action" @click="navigate">
          <span v-if="item.icon" :class="item.icon" class="text-xl" />
          <span>{{ item.label }}</span>
        </a>
      </router-link>

      <a
        v-else
        v-ripple
        :href="item.url"
        :target="item.target"
        v-bind="props.action"
      >
        <span v-if="item.icon" :class="item.icon" class="text-xl" />
        <span>{{ item.label }}</span>
        <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down" />
      </a>
    </template>
  </Menubar>
</template>
<style>
.no-hover:hover {
  background-color: inherit !important;
}
</style>
