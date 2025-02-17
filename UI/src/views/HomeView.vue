<script setup lang="ts">
import Button from "primevue/button"
import Panel from "primevue/panel"
import Card from "primevue/card"
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
    <section class="px-8 py-6 flex justify-content-center gap-4">
      <Card class="w-5 md:w-3 lg:w-3">
        <template #header>
          <img alt="user header" src="/IMC&Calories.png" class="w-full" />
        </template>
        <template #title>Calcule</template>
        <template #subtitle>Ton IMC & Tes besoins en calories</template>
        <template #content>
          <ul class="m-0">
            <li>
              <strong>IMC :</strong> Indicateur du poids idéal selon la taille,
              utile pour évaluer les risques de surpoids ou de maigreur.
            </li>
            <li>
              <strong>Besoins caloriques :</strong> Quantité d'énergie
              nécessaire au corps selon l'âge, le poids et l'activité.
            </li>
          </ul>
        </template>
      </Card>
      <Card class="w-5 md:w-3 lg:w-3">
        <template #header>
          <img alt="user header" src="/Evolution.png" class="w-full" />
        </template>
        <template #title>Analyse</template>
        <template #subtitle>L'évolution de ton corps</template>
        <template #content>
          <ul class="m-0">
            <li>
              Visualise tes progrès pour rester motivé et ajuster tes efforts en
              fonction des résultats obtenus.
            </li>
            <li>
              Analyse ton évolution pour identifier les tendances et adapter ton
              alimentation et ton activité physique efficacement.
            </li>
          </ul>
        </template>
      </Card>
    </section>
  </div>
</template>
