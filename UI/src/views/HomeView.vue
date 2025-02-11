<script setup lang="ts">
import Button from "primevue/button"
import Panel from "primevue/panel"
import { PRESENTATION_TEXT, SUBTITLE, TITLE } from "@/assets/js/constants"
</script>

<template>
  <div class="mx-8">
    <section class="text-center">
      <h1 class="text-6xl font-bold">
        {{ TITLE }}
      </h1>
      <p class="text-xl mt-3 opacity-90">
        {{ SUBTITLE }}
      </p>
      <div class="flex gap-3 justify-content-center mt-4">
        <Button
          as="router-link"
          label="Calculer mon IMC 📊"
          to="/calculatrice-imc"
          class="no-underline font-semibold"
          severity="primary"
          rounded
          raised
        />
        <Button
          as="router-link"
          label="Besoins en calories 🔥"
          to="/calculatrice-calories"
          class="no-underline font-semibold"
          severity="secondary"
          rounded
          raised
        />
      </div>
    </section>
    <section class="text-center px-8 py-6">
      <h2 class="text-3xl font-bold">
        Pourquoi choisir <span class="text-blue-500">NextShape</span> ?
      </h2>
      <Panel class="shadow-3 mt-4 border-round-lg">
        <p class="text-lg text-700 mt-3 leading-loose">
          {{ PRESENTATION_TEXT }}
        </p>
      </Panel>
    </section>
  </div>
</template>
