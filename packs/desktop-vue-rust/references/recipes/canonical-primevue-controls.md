# Recipe: Canonical PrimeVue Controls & Nora Theming

Authoritative visual and component patterns for PrimeVue v4 with the Nora theme in desktop applications.

---

## 1. Interactive Form Controls

Always use PrimeVue v4 components instead of raw HTML elements:

| Control | Correct PrimeVue Component | Banned Raw HTML | Example Usage |
|---|---|---|---|
| Action trigger | `<Button label="..." />` | `<button>` | `<Button label="Save" severity="primary" size="small" />` |
| Text input | `<InputText v-model="..." />` | `<input type="text">` | `<InputText v-model="name" size="small" placeholder="..." />` |
| Number input | `<InputNumber v-model="..." />` | `<input type="number">` | `<InputNumber v-model="port" :min="1" :max="65535" size="small" />` |
| Dropdown select | `<Select v-model="..." :options="..." />` | `<select>` | `<Select v-model="selected" :options="options" size="small" />` |
| Toggle switch | `<ToggleSwitch v-model="..." />` | `<input type="checkbox">` | `<ToggleSwitch v-model="enableSsl" />` |
| Multi-line text | `<Textarea v-model="..." />` | `<textarea>` | `<Textarea v-model="description" rows="3" autoResize />` |

---

## 2. Tooltips & Hover Hints

**NEVER use native HTML `title="..."` attributes for tooltips.**
Always use PrimeVue's `v-tooltip` directive:

```vue
<!-- Correct: PrimeVue v-tooltip with positions -->
<Button icon="pi pi-refresh" v-tooltip.top="'Refresh Table'" />
<Button icon="pi pi-trash" severity="danger" v-tooltip.bottom="'Delete Item'" />
<span v-tooltip.left="'Connection status'">Online</span>

<!-- WRONG: Flagged by verify_shift_left.py -->
<Button icon="pi pi-refresh" title="Refresh Table" />
<button title="Click me">Submit</button>
```

---

## 3. Borderless Form Layouts

Use a borderless, two-column grouping for forms instead of heavy container boxes or `<hr>` lines:

```vue
<div class="grid grid-cols-1 md:grid-cols-12 gap-6 py-4 border-b border-(--border)/40 last:border-b-0">
  <!-- Left column: Title & Description -->
  <div class="md:col-span-4 flex flex-col gap-1">
    <h3 class="text-sm font-semibold text-(--text-primary)">Network Settings</h3>
    <p class="text-xs text-(--text-muted)">Configure port numbers and target endpoints.</p>
  </div>

  <!-- Right column: Controls -->
  <div class="md:col-span-8 flex flex-col gap-4">
    <div class="flex items-center justify-between">
      <label class="text-xs font-medium text-(--text-secondary)">Enable SSL</label>
      <ToggleSwitch v-model="form.ssl" />
    </div>
    <div class="flex flex-col gap-1.5">
      <label class="text-xs font-medium text-(--text-secondary)">Port</label>
      <InputNumber v-model="form.port" size="small" />
    </div>
  </div>
</div>
```

---

## 4. Modal Dialogs & Confirmations

```vue
<script setup lang="ts">
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

const visible = defineModel<boolean>('visible')
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    header="Edit Configuration"
    :style="{ width: '32rem' }"
    :breakpoints="{ '640px': '90vw' }"
  >
    <div class="py-2">
      <!-- Modal body content -->
    </div>

    <template #footer>
      <Button label="Cancel" severity="secondary" variant="text" size="small" @click="visible = false" />
      <Button label="Save" severity="primary" size="small" @click="save" />
    </template>
  </Dialog>
</template>
```
