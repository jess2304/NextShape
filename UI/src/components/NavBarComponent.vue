<script setup lang="ts">
import Menubar from "primevue/menubar"
import Button from "primevue/button"
import { RouterLink, useRouter } from "vue-router"
import { NAVBAR_ELEMENTS } from "@/assets/js/constants"
import NavBarConnexionComponent from "@/components/NavBarConnexionComponent.vue"

const router = useRouter()
</script>
<template>
  <Menubar :model="NAVBAR_ELEMENTS">
    <template #start>
      <img
        src="/nextshape.png"
        alt="NextShape Icon"
        class="w-1 flex-shrink-0" />
      <Button
        text
        label="NextShape"
        class="text-2xl no-hover p-0"
        @click="router.push('/')"
    /></template>
    <template #item="{ item, props, hasSubmenu }">
      <RouterLink
        v-if="item.route"
        v-slot="{ href, navigate }"
        :to="item.route"
        custom
      >
        <a v-ripple :href="href" v-bind="props.action" @click="navigate">
          <span v-if="item.icon" :class="item.icon" class="text-lg" />
          <span>{{ item.label }}</span>
        </a>
      </RouterLink>

      <a
        v-else
        v-ripple
        :href="item.url"
        :target="item.target"
        v-bind="props.action"
      >
        <span v-if="item.icon" :class="item.icon" class="text-lg" />
        <span>{{ item.label }}</span>
        <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down" />
      </a>
    </template>
    <template #end>
      <NavBarConnexionComponent />
    </template>
  </Menubar>
</template>
<style>
.no-hover:hover {
  background-color: inherit !important;
}
</style>
