# Recipe: Canonical Desktop Data View (View, Table & Drawer)

Standard desktop view layout consisting of a header, filter toolbar, flat PrimeVue DataTable, and progressive disclosure DetailsDrawer.

---

## 1. Page View Layout (`src/views/EntityListView.vue`)

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import ViewLayout from '@/components/layout/ViewLayout.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Skeleton from 'primevue/skeleton'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EntityDetailsDrawer from '@/components/entity/EntityDetailsDrawer.vue'
import { useEntityStore } from '@/stores/entityStore'

const store = useEntityStore()
const searchQuery = ref('')
const selectedEntity = ref<Entity | null>(null)
const isDrawerOpen = ref(false)

const filteredItems = computed(() => {
  if (!searchQuery.value.trim()) return store.items
  return store.items.filter(item =>
    item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

function openDetails(item: Entity) {
  selectedEntity.value = item
  isDrawerOpen.value = true
}
</script>

<template>
  <ViewLayout title="Entities">
    <template #actions>
      <Button
        label="Refresh"
        icon="pi pi-refresh"
        size="small"
        variant="outlined"
        @click="store.fetch()"
      />
    </template>

    <!-- Filter Toolbar -->
    <div class="flex items-center gap-3 mb-4">
      <InputText
        v-model="searchQuery"
        placeholder="Filter entities..."
        variant="filled"
        size="small"
        class="min-w-64"
      />
    </div>

    <!-- Flat Data Table -->
    <div class="border border-(--border) rounded-lg overflow-hidden bg-(--bg-card)">
      <DataTable
        :value="filteredItems"
        :loading="store.isLoading"
        paginator
        :rows="15"
        size="small"
        responsiveLayout="scroll"
      >
        <template #empty>
          <div class="p-8 text-center text-muted-color">No entities found.</div>
        </template>

        <template #loading>
          <div class="p-4 space-y-2">
            <Skeleton width="100%" height="2rem" />
            <Skeleton width="100%" height="2rem" />
          </div>
        </template>

        <Column field="name" header="Name" sortable>
          <template #body="{ data }">
            <span
              class="font-medium text-primary hover:text-accent cursor-pointer"
              @click="openDetails(data)"
            >
              {{ data.name }}
            </span>
          </template>
        </Column>

        <Column field="status" header="Status" sortable>
          <template #body="{ data }">
            <StatusBadge :status="data.status" />
          </template>
        </Column>

        <Column header="Actions" alignFrozen="right" frozen>
          <template #body="{ data }">
            <Button
              icon="pi pi-ellipsis-v"
              variant="text"
              severity="secondary"
              size="small"
              v-tooltip="'Entity actions'"
              @click="openDetails(data)"
            />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Details Drawer -->
    <EntityDetailsDrawer
      v-model:visible="isDrawerOpen"
      :entity="selectedEntity"
    />
  </ViewLayout>
</template>
```

---

## 2. Details Drawer Component (`src/components/entity/EntityDetailsDrawer.vue`)

```vue
<script setup lang="ts">
import Drawer from 'primevue/drawer'
import Button from 'primevue/button'

defineProps<{
  entity: Entity | null
}>()

const visible = defineModel<boolean>('visible')
</script>

<template>
  <Drawer
    v-model:visible="visible"
    position="right"
    class="w-full md:w-160!"
  >
    <template #header>
      <div class="flex items-center gap-2">
        <h3 class="text-lg font-bold">{{ entity?.name ?? 'Details' }}</h3>
      </div>
    </template>

    <div v-if="entity" class="space-y-6 p-4">
      <div>
        <span class="text-xs uppercase tracking-wider text-muted-color font-semibold">Status</span>
        <p class="text-sm mt-1">{{ entity.status }}</p>
      </div>

      <div>
        <span class="text-xs uppercase tracking-wider text-muted-color font-semibold">Metadata</span>
        <pre class="bg-(--bg-app) p-3 rounded font-mono text-xs mt-1 overflow-x-auto">{{ JSON.stringify(entity, null, 2) }}</pre>
      </div>
    </div>
  </Drawer>
</template>
```
