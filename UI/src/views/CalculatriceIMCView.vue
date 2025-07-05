<script setup lang="ts">
import Fieldset from "primevue/fieldset"
import Avatar from "primevue/avatar"
import InputNumber from "primevue/inputnumber"
import Button from "primevue/button"
import Panel from "primevue/panel"
import Tag from "primevue/tag"
import { useProgressRecord } from "@/stores/progressRecordStore"
import { computed, ref } from "vue"
import { useToast } from "primevue/usetoast"
import Message from "primevue/message"

const progressStore = useProgressRecord()
const toast = useToast()

const weight_kg = ref<number>()
const height_cm = ref<number>()

const imc = computed(() => progressStore.progressRecord?.imc ?? null)
const imcResult = computed(() => {
  if (!imc.value) return null
  if (imc.value < 18.5) return { label: "Maigreur", severity: "warn" }
  if (imc.value < 25)
    return { label: "Corpulence normale", severity: "success" }
  if (imc.value < 30) return { label: "Surpoids", severity: "warn" }
  return { label: "Obésité", severity: "danger" }
})

const submit = async () => {
  try {
    await progressStore.calculateIMC(
      weight_kg.value || -1,
      height_cm.value || -1
    )
    toast.add({
      severity: "success",
      summary: "IMC enregistré",
      detail: `Votre IMC a été calculé et enregistré`,
      life: 5000,
    })
  } catch (error: any) {
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail:
        error?.response?.data?.errors?.non_field_errors?.[0] ||
        error?.response?.data?.message ||
        "Échec de l'enregistrement de l'IMC",
      life: 5000,
    })
  }
}

const severityIMC = computed(() => {
  const imc = progressStore.progressRecord?.imc
  if (imc) {
    if (imc >= 18.5 && imc <= 24.9) return "success"
    else if (imc < 18.5 || (imc >= 25 && imc <= 29.9)) return "warn"
    else return "danger"
  }
})
</script>

<template>
  <Fieldset
    :pt="{
      legend: { class: 'bg-transparent' },
      root: { class: 'shadow-2 border-round-lg p-4' },
    }"
  >
    <template #legend>
      <div class="flex items-center pl-2 gap-3">
        <Avatar image="/Calculatrice.png" shape="circle" />
        <span class="font-bold text-2xl">Calculatrice d'IMC</span>
      </div>
    </template>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="space-y-4">
        <div class="formgrid grid mt-4">
          <div class="field col-12 md:col-6">
            <label for="taille">Taille (cm)</label>
            <InputNumber
              v-model="height_cm"
              inputId="taille"
              suffix=" cm"
              showButtons
              class="w-full"
              fluid
              :minFractionDigits="1"
              :maxFractionDigits="1"
            />
          </div>

          <div class="field col-12 md:col-6">
            <label for="poids">Poids (kg)</label>
            <InputNumber
              v-model="weight_kg"
              inputId="poids"
              suffix=" kg"
              showButtons
              class="w-full"
              :minFractionDigits="1"
              :maxFractionDigits="1"
            />
          </div>

          <div class="col-12 md:col-6">
            <Button
              label="Calculer & Enregistrer"
              icon="pi pi-check"
              class="p-button-success"
              @click="submit"
            />
          </div>
        </div>
        <div class="block mt-2" v-if="imcResult">
          <Message :severity="imcResult.severity">
            Votre IMC est : <strong>{{ imc }}</strong
            >. Selon les recommandations de l'OMS vous êtes en :
            <strong>{{ imcResult.label }}</strong>
          </Message>
        </div>
      </div>
      <div class="w-full md:w-1/2 space-y-3">
        <h3 class="text-xl font-semibold text-gray-800 flex items-center gap-2">
          Qu'est-ce que l'IMC ?
        </h3>
        <div class="space-y-4 text-gray-700 leading-relaxed">
          <p>
            <strong>L'indice de masse corporelle</strong> (IMC) est une mesure
            utilisée pour évaluer la corpulence d'un individu à partir de son
            poids et de sa taille.
          </p>
          <p>
            Il est calculé selon la formule :
            <br />
            <span class="font-semibold text-blue-600"
              >IMC = poids (kg) / taille² (m)</span
            >
          </p>
          <p>
            Un IMC anormal peut être associé à des risques pour la santé, mais
            il ne prend pas en compte la masse musculaire, la répartition des
            graisses ou l'âge.
          </p>
        </div>
        <Panel
          header="Selon les recommandations de l'OMS :"
          class="border-round shadow-2"
        >
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
            <div
              class="flex items-center justify-between gap-2 p-2 bg-gray-50 border-round shadow-sm"
            >
              <span><strong>IMC &lt; 18,5</strong></span>
              <Tag severity="warn" value="Maigreur" />
            </div>
            <div
              class="flex items-center justify-between gap-2 p-2 bg-gray-50 border-round shadow-sm"
            >
              <span><strong>IMC de 18,5 à 24,9</strong></span>
              <Tag severity="success" value="Normal" />
            </div>
            <div
              class="flex items-center justify-between gap-2 p-2 bg-gray-50 border-round shadow-sm"
            >
              <span><strong>IMC de 25 à 29,9</strong></span>
              <Tag severity="warn" value="Surpoids" />
            </div>
            <div
              class="flex items-center justify-between gap-2 p-2 bg-gray-50 border-round shadow-sm"
            >
              <span><strong>IMC&ge; 30</strong></span>
              <Tag severity="danger" value="Obésité" />
            </div>
          </div>
        </Panel>
      </div>
    </div>
  </Fieldset>
</template>
