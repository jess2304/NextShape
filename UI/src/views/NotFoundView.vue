<script setup lang="ts">
import NsButton from "@/components/ui/NsButton.vue"
</script>

<template>
  <section class="not-found">
    <span class="error-code" aria-hidden="true">404</span>
    <span class="eyebrow">UN PETIT DÉTOUR</span>
    <h1>Cette page est introuvable.</h1>
    <p>
      Le lien a peut-être changé. Retrouvez votre chemin depuis l’accueil de
      NextShape.
    </p>
    <NsButton
      as="router-link"
      label="Retour à l’accueil"
      icon="pi pi-arrow-left"
      to="/"
    />
  </section>
</template>

<style scoped>
.not-found {
  max-width: 520px;
  margin: clamp(2rem, 8vh, 6rem) auto;
  text-align: center;
}
.error-code {
  display: block;
  color: #dce6d9;
  font-size: clamp(6rem, 22vw, 10rem);
  font-weight: 650;
  line-height: 1;
  letter-spacing: -0.09em;
  margin-bottom: 1.7rem;
}
.eyebrow {
  font-size: 0.7rem;
  color: #1d4d40;
  letter-spacing: 0.15em;
  font-weight: 700;
}
h1 {
  font-size: clamp(1.6rem, 4vw, 2.2rem);
  line-height: 1.2;
  letter-spacing: -0.04em;
  margin: 1rem 0;
}
p {
  color: #69766f;
  line-height: 1.7;
  font-size: 0.94rem;
  margin: 0 auto 1.8rem;
}
</style>
