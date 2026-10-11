<script setup lang="ts">
import { isCancel } from "axios"
import { useProgressRecords } from "@/stores/progressRecordsStore"
import { onMounted, onUnmounted, ref } from "vue"
import {
  formatDate,
  resolveApiErrorMessage,
  resolveApiMessage,
  showToast,
} from "@/assets/js/utils"
import { ACTIVITY_DESCRIPTIONS, ACTIVITY_LEVELS } from "@/assets/js/constants"
import { useToast } from "primevue"
import DataTable from "primevue/datatable"
import Column from "primevue/column"
import NsButton from "@/components/ui/NsButton.vue"
import NsSelect from "@/components/ui/NsSelect.vue"
import NsBadge from "@/components/ui/NsBadge.vue"
import NsNumberInput from "@/components/ui/NsNumberInput.vue"
import NsCard from "@/components/ui/NsCard.vue"
import NsEmptyState from "@/components/ui/NsEmptyState.vue"
import NsSkeleton from "@/components/ui/NsSkeleton.vue"
import PageHeader from "@/components/layout/PageHeader.vue"
import MobileEditModal from "@/components/MobileEditModal.vue"

const mobileQuery = window.matchMedia("(max-width: 1100px)")
const isMobile = ref(mobileQuery.matches)
const updateLayout = (event: MediaQueryListEvent) => {
  isMobile.value = event.matches
}
onMounted(() => mobileQuery.addEventListener("change", updateLayout))
onUnmounted(() => mobileQuery.removeEventListener("change", updateLayout))
const isLoading = ref(true)
const loadError = ref("")

// Store
const progressRecordsStore = useProgressRecords()
const toast = useToast()
const editingRows = ref([])
// Keep request state local to the presentation; session ownership stays in the store.
const loadRecords = async () => {
  isLoading.value = true
  loadError.value = ""
  try {
    await progressRecordsStore.getProgressRecords()
  } catch (error: any) {
    if (isCancel(error)) return
    loadError.value = resolveApiErrorMessage(
      error,
      "Échec du chargement de votre historique"
    )
    showToast(toast, "error", "Erreur", loadError.value)
  } finally {
    isLoading.value = false
  }
}
onMounted(loadRecords)

const goalOptions: Array<Record<string, string>> = [
  { label: "Maintien", value: "maintien" },
  { label: "Perte de poids", value: "perte" },
  { label: "Prise de masse", value: "prise" },
]
const goalLabels: Record<string, string> = {
  maintien: "Maintien",
  perte: "Perte de poids",
  prise: "Prise de masse",
}
type BadgeTone = "neutral" | "success" | "warning" | "danger"
const goalTone: Record<string, BadgeTone> = {
  maintien: "neutral",
  perte: "warning",
  prise: "success",
}

const activityLabels = Object.fromEntries(
  ACTIVITY_LEVELS.map((lvl) => [lvl.value, lvl.label])
)

const activityTone: Record<string, BadgeTone> = {
  sedentaire: "neutral",
  leger: "neutral",
  modere: "success",
  intense: "warning",
  tres_intense: "danger",
}

const onRowEditSave = async (event: any) => {
  const { newData } = event

  const requiredFields = ["weight_kg", "height_cm", "goal", "activity_level"]

  const hasEmpty = requiredFields.some((field) => {
    return (
      newData[field] === null ||
      newData[field] === "" ||
      newData[field] === undefined
    )
  })

  if (hasEmpty) {
    toast.add({
      severity: "warn",
      summary: "Champs invalides",
      detail: "Tous les champs doivent être remplis.",
      life: 3000,
    })
    event.originalEvent.preventDefault()
    return
  }

  try {
    const response = await progressRecordsStore.updateRecord(newData.id, {
      weight_kg: newData.weight_kg,
      height_cm: newData.height_cm,
      goal: newData.goal,
      activity_level: newData.activity_level,
    })
    showToast(
      toast,
      "success",
      "Succès",
      resolveApiMessage(response, "La mise à jour a été faite avec succès")
    )
  } catch (error: any) {
    if (isCancel(error)) return
    showToast(
      toast,
      "error",
      "Erreur",
      resolveApiErrorMessage(error, "Échec de l'enregistrement")
    )
  }
}

const deleteRecord = async (id: number) => {
  try {
    const response = await progressRecordsStore.deleteRecord(id)
    toast.add({
      severity: "success",
      summary: "Supprimé",
      detail: resolveApiMessage(response, "Enregistrement supprimé"),
      life: 3000,
    })
  } catch (err) {
    if (isCancel(err)) return
    toast.add({
      severity: "error",
      summary: "Erreur",
      detail: resolveApiErrorMessage(
        err,
        "Impossible de supprimer l'enregistrement"
      ),
      life: 3000,
    })
  }
}

const editMobileVisible = ref(false)
const editingId = ref<number | null>(null)

const openMobileEdit = (recordId: number) => {
  editingId.value = recordId
  editMobileVisible.value = true
}
</script>

<template>
  <div class="history-page">
    <PageHeader
      eyebrow="Votre parcours"
      title="Historique de calculs"
      description="Retrouvez vos mesures et les repères nutritionnels calculés au fil du temps."
    >
      <template #actions>
        <RouterLink to="/calculatrice-calories" class="history-new-link">
          <i class="pi pi-plus" aria-hidden="true" /> Nouveau calcul
        </RouterLink>
      </template>
    </PageHeader>

    <NsCard
      v-if="isLoading"
      class="history-loading"
      aria-busy="true"
      aria-label="Chargement de l'historique"
    >
      <NsSkeleton width="11rem" height="1.25rem" />
      <NsSkeleton v-for="index in 4" :key="index" height="3rem" />
      <span class="history-status" role="status"
        >Chargement de votre historique…</span
      >
    </NsCard>
    <NsCard v-else-if="loadError">
      <NsEmptyState
        icon="pi pi-exclamation-circle"
        title="L'historique n'a pas pu être chargé"
        :description="loadError"
      >
        <NsButton
          label="Réessayer"
          icon="pi pi-refresh"
          outlined
          @click="loadRecords"
        />
      </NsEmptyState>
    </NsCard>
    <NsCard v-else-if="!progressRecordsStore.progressRecords.length">
      <NsEmptyState
        icon="pi pi-history"
        title="Votre parcours commence ici"
        description="Vos calculs enregistrés apparaîtront ici. Vous pourrez retrouver vos mesures et les modifier à tout moment."
      >
        <RouterLink to="/calculatrice-calories" class="history-new-link"
          >Faire mon premier calcul
          <i class="pi pi-arrow-right" aria-hidden="true"
        /></RouterLink>
      </NsEmptyState>
    </NsCard>
    <template v-else>
      <div class="history-caption">
        <span
          >{{ progressRecordsStore.progressRecords.length }} enregistrement{{
            progressRecordsStore.progressRecords.length > 1 ? "s" : ""
          }}</span
        >
        <span>Vos données, au même endroit.</span>
      </div>
      <div v-if="isMobile" class="history-records">
        <NsCard
          v-for="record in progressRecordsStore.progressRecords"
          :key="record.id"
          class="history-record"
        >
          <div class="record-heading">
            <div>
              <span class="record-label">Calcul enregistré</span>
              <h2>{{ formatDate(record.date ?? "") }}</h2>
            </div>
            <NsBadge :tone="goalTone[record.goal ?? '']">{{
              goalLabels[record.goal ?? ""] ?? "Objectif non renseigné"
            }}</NsBadge>
          </div>
          <dl class="record-metrics">
            <div>
              <dt>Poids</dt>
              <dd>{{ record.weight_kg ?? "—" }} <small>kg</small></dd>
            </div>
            <div>
              <dt>Taille</dt>
              <dd>{{ record.height_cm ?? "—" }} <small>cm</small></dd>
            </div>
            <div>
              <dt>IMC</dt>
              <dd>{{ record.imc?.toFixed(1) ?? "—" }}</dd>
            </div>
          </dl>
          <dl class="record-details">
            <div>
              <dt>Activité physique</dt>
              <dd>
                <NsBadge :tone="activityTone[record.activity_level ?? '']">{{
                  activityLabels[record.activity_level ?? ""] ??
                  "Non renseignée"
                }}</NsBadge>
              </dd>
            </div>
            <div>
              <dt>Métabolisme de base (BMR)</dt>
              <dd>{{ record.bmr ?? "—" }} kcal</dd>
            </div>
            <div>
              <dt>Dépense quotidienne (TDEE)</dt>
              <dd>{{ record.tdee ?? "—" }} kcal</dd>
            </div>
          </dl>
          <div class="record-target">
            <span>Calories recommandées</span
            ><strong
              >{{ record.calories_recommandees ?? "—" }}
              <small>kcal / jour</small></strong
            >
          </div>
          <div class="record-actions">
            <NsButton
              label="Modifier"
              icon="pi pi-pencil"
              severity="secondary"
              text
              @click="openMobileEdit(record.id)"
            />
            <NsButton
              label="Supprimer"
              icon="pi pi-trash"
              text
              severity="danger"
              @click="deleteRecord(record.id)"
            />
          </div>
        </NsCard>
      </div>
      <NsCard v-else class="history-table-card">
        <DataTable
          :value="progressRecordsStore.progressRecords"
          dataKey="id"
          responsiveLayout="scroll"
          editMode="row"
          v-model:editingRows="editingRows"
          @row-edit-save="onRowEditSave"
          paginator
          :rows="5"
          :rowsPerPageOptions="[5, 10, 20, 50]"
          class="history-table"
          :tableStyle="{ minWidth: '70rem' }"
        >
          <Column field="date" header="Date"
            ><template #body="{ data }"
              ><span class="table-date">{{
                formatDate(data.date)
              }}</span></template
            ></Column
          >
          <Column field="weight_kg" header="Poids">
            <template #body="{ data }">{{ data.weight_kg ?? "—" }} kg</template>
            <template #editor="{ data, field }"
              ><NsNumberInput
                v-model="data[field]"
                aria-label="Poids en kilogrammes"
                suffix=" kg"
                :minFractionDigits="1"
                :maxFractionDigits="1"
                :min="0"
                showButtons
                fluid
                class="table-number-input"
            /></template>
          </Column>
          <Column field="height_cm" header="Taille">
            <template #body="{ data }">{{ data.height_cm ?? "—" }} cm</template>
            <template #editor="{ data, field }"
              ><NsNumberInput
                v-model="data[field]"
                aria-label="Taille en centimètres"
                suffix=" cm"
                :minFractionDigits="1"
                :maxFractionDigits="1"
                :min="0"
                showButtons
                fluid
                class="table-number-input"
            /></template>
          </Column>
          <Column field="activity_level" header="Activité physique">
            <template #body="{ data }"
              ><NsBadge :tone="activityTone[data.activity_level]">{{
                activityLabels[data.activity_level] ?? "Non renseignée"
              }}</NsBadge></template
            >
            <template #editor="{ data, field }">
              <NsSelect
                v-model="data[field]"
                :options="ACTIVITY_LEVELS"
                option-label="label"
                option-value="value"
                placeholder="Choisir"
                aria-label="Activité physique"
                class="table-select-input"
              >
                <template #option="slotProps"
                  ><div class="activity-option">
                    <span>{{ slotProps.option.label }}</span
                    ><small>{{
                      ACTIVITY_DESCRIPTIONS[slotProps.option.value]
                    }}</small>
                  </div></template
                >
              </NsSelect>
            </template>
          </Column>
          <Column field="goal" header="Objectif">
            <template #body="{ data }"
              ><NsBadge :tone="goalTone[data.goal]">{{
                goalLabels[data.goal] ?? "Non renseigné"
              }}</NsBadge></template
            >
            <template #editor="{ data, field }"
              ><NsSelect
                v-model="data[field]"
                :options="goalOptions"
                option-label="label"
                option-value="value"
                aria-label="Objectif"
                class="table-select-input"
            /></template>
          </Column>
          <Column field="imc" header="IMC"
            ><template #body="{ data }">{{
              data.imc?.toFixed(1) ?? "—"
            }}</template></Column
          >
          <Column field="bmr" header="BMR"
            ><template #body="{ data }"
              >{{ data.bmr ?? "—" }} kcal</template
            ></Column
          >
          <Column field="tdee" header="TDEE"
            ><template #body="{ data }"
              >{{ data.tdee ?? "—" }} kcal</template
            ></Column
          >
          <Column field="calories_recommandees" header="Calories"
            ><template #body="{ data }"
              ><strong class="table-target"
                >{{ data.calories_recommandees ?? "—" }} kcal</strong
              ></template
            ></Column
          >
          <Column header=""
            ><template #body="{ data }"
              ><NsButton
                icon="pi pi-trash"
                severity="danger"
                text
                aria-label="Supprimer cet enregistrement"
                @click="deleteRecord(data.id)" /></template
          ></Column>
          <Column
            :rowEditor="true"
            header="Modifier"
            style="min-width: 7rem"
            bodyStyle="text-align:center"
          />
        </DataTable>
        <p class="history-table-help">
          BMR : métabolisme de base · TDEE : dépense énergétique quotidienne.
        </p>
      </NsCard>
    </template>
    <MobileEditModal
      v-model:visible="editMobileVisible"
      v-model:recordId="editingId"
    />
  </div>
</template>

<style scoped>
.history-page {
  display: grid;
  gap: 1.5rem;
  min-width: 0;
}
.history-new-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  min-height: 2.75rem;
  padding: 0.7rem 1rem;
  border-radius: 0.65rem;
  background: var(--ns-primary);
  color: #fff;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.875rem;
}
.history-new-link:hover {
  background: #163d32;
}
.history-new-link:focus-visible {
  outline: 3px solid #91b5a5;
  outline-offset: 3px;
}
.history-loading {
  display: grid;
  gap: 1rem;
}
.history-status,
.history-caption {
  color: var(--ns-muted);
  font-size: 0.875rem;
}
.history-caption {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem;
}
.history-records {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}
.record-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.record-label {
  font-size: 0.75rem;
  color: var(--ns-muted);
}
.record-heading h2 {
  margin: 0.2rem 0 0;
  font-size: 1rem;
  color: var(--ns-ink);
}
.record-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
  padding: 1.25rem 0;
  margin: 1rem 0;
  border-block: 1px solid var(--ns-border);
}
.record-metrics dt,
.record-details dt {
  font-size: 0.8rem;
  color: var(--ns-muted);
}
.record-metrics dd {
  margin: 0.3rem 0 0;
  font-size: 1.35rem;
  color: var(--ns-ink);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.record-metrics small {
  font-size: 0.75rem;
  font-weight: 400;
  color: var(--ns-muted);
}
.record-details {
  display: grid;
  gap: 0.8rem;
  margin: 0;
}
.record-details > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.record-details dd {
  margin: 0;
  text-align: right;
  font-size: 0.82rem;
  font-variant-numeric: tabular-nums;
}
.record-target {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.9rem;
  background: var(--ns-sage);
  border-radius: 0.65rem;
  margin-top: 1.25rem;
  color: var(--ns-primary);
  font-size: 0.8rem;
}
.record-target strong {
  font-size: 1rem;
  font-variant-numeric: tabular-nums;
}
.record-target small {
  font-size: 0.7rem;
  font-weight: 400;
}
.record-actions {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.9rem -0.5rem -0.4rem;
}
.history-table-card {
  min-width: 0;
  overflow: hidden;
  padding: 0;
}
.history-table {
  font-size: 0.8rem;
  font-variant-numeric: tabular-nums;
}
.history-table :deep(th),
.history-table :deep(td) {
  white-space: nowrap;
  padding-block: 1rem;
}
.history-table :deep(.p-datatable-table-container) {
  overflow-x: auto;
}
.table-date {
  font-weight: 500;
}
.table-target {
  color: var(--ns-primary);
}
.table-number-input {
  min-width: 7rem;
  max-width: 9rem;
}
.table-select-input {
  min-width: 10rem;
}
.activity-option {
  display: grid;
  gap: 0.3rem;
  max-width: 17rem;
  white-space: normal;
}
.activity-option > span {
  font-weight: 600;
}
.activity-option small {
  color: var(--ns-muted);
  line-height: 1.4;
}
.history-table-help {
  margin: 0;
  padding: 0.9rem 1.25rem;
  border-top: 1px solid var(--ns-border);
  color: var(--ns-muted);
  font-size: 0.75rem;
}
@media (max-width: 700px) {
  .history-records {
    grid-template-columns: minmax(0, 1fr);
  }
  .history-caption > span:last-child {
    display: none;
  }
}
</style>
