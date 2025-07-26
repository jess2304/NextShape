<script setup lang="ts">
import Button from "primevue/button"
import { Panel } from "primevue"
import { TITLE, SUBTITLE, PRESENTATION_TEXT } from "@/assets/js/constants"
</script>

<template>
  <div>
    <section class="p-fluid md:px-8">
      <div class="grid align-items-center justify-content-center">
        <div class="col-12 md:col-6 text-center md:text-left">
          <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-3">
            {{ TITLE }}
          </h1>
          <p v-html="SUBTITLE" class="text-xl text-gray-600 mb-5" />
          <div
            class="flex flex-column sm:flex-row gap-3 justify-content-center md:justify-content-start"
          >
            <Button
              as="router-link"
              to="/calculatrice-imc"
              label="Calculer mon IMC"
              severity="primary"
              rounded
              raised
              class="no-underline font-semibold w-full sm:w-auto"
            />
            <Button
              as="router-link"
              to="/calculatrice-calories"
              label="Calculer mes calories"
              severity="secondary"
              rounded
              raised
              class="no-underline font-semibold w-full sm:w-auto"
            />
          </div>
        </div>
        <div
          class="col-12 md:col-6 flex justify-content-center md:justify-content-end mt-5 md:mt-0"
        >
          <img
            src="/hero-nextshape.png"
            alt="Illustration NextShape"
            class="w-11 md:w-20 lg:w-15 shadow-3 border-round-xl"
          />
        </div>
      </div>
    </section>
    <section class="mt-7 px-4 md:px-8 text-center">
      <div class="flex justify-content-center">
        <Panel
          header=""
          class="w-full md:w-10 lg:w-full shadow-3 border-round-xl"
        >
          <p
            v-html="PRESENTATION_TEXT"
            class="text-base md:text-lg text-gray-700 leading-normal mt-2"
          />
        </Panel>
      </div>
    </section>
  </div>
</template>
