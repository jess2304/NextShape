<script setup lang="ts">
const logo = `${import.meta.env.BASE_URL}nextshape.png`
</script>

<template>
  <RouterLink to="/" class="brand-mark" aria-label="NextShape, accueil">
    <img :src="logo" alt="" width="40" height="40" />
    <span>NextShape<span class="brand-mark__dot">.</span></span>
  </RouterLink>
</template>

<style scoped>
.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--ns-primary);
  text-decoration: none;
  font-size: 1.35rem;
  font-weight: 650;
  letter-spacing: -0.065em;
  flex-shrink: 0;
}
.brand-mark img {
  width: 2.5rem;
  height: 2.5rem;
  object-fit: contain;
}
.brand-mark__dot {
  color: #799c6f;
}
</style>
