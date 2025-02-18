<script setup>
import { ref, onMounted } from "vue"
import { fetchHealthRecords } from "../services/apiService"

const healthRecords = ref([])

onMounted(async () => {
  healthRecords.value = await fetchHealthRecords()
})
</script>

<template>
  <div>
    <h2 class="text-primary">Données des utilisateurs</h2>
    <ul v-if="healthRecords.length">
      <li v-for="record in healthRecords" :key="record.id">
        <strong>{{ record.user }}</strong> | {{ record.weight }} kg |
        {{ record.height }} cm | {{ record.activity_level }}
      </li>
    </ul>
    <p v-else>Aucune donnée disponible...</p>
  </div>
</template>
