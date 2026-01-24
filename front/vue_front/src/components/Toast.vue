<template>
  <Transition
    enter-active-class="transition-all duration-500"
    enter-from-class="translate-y-20 opacity-0"
    enter-to-class="translate-y-0 opacity-100"
    leave-active-class="transition-all duration-500"
    leave-from-class="translate-y-0 opacity-100"
    leave-to-class="translate-y-20 opacity-0"
  >
    <div 
      v-if="visible"
      class="fixed bottom-6 right-6 px-4 py-3 rounded-lg shadow-lg flex items-center z-50"
      :class="type === 'warning' ? 'bg-warning text-white' : 'bg-primary text-white'"
    >
      <i :class="type === 'warning' ? 'fas fa-exclamation-circle mr-2' : 'fas fa-refresh mr-2'"></i>
      <span>{{ message }}</span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  message: string
  type?: 'success' | 'warning'
  duration?: number
}>()

const visible = ref(false)
const timer = ref<number | null>(null)

const show = () => {
  visible.value = true
  if (timer.value) {
    clearTimeout(timer.value)
  }
  timer.value = window.setTimeout(() => {
    visible.value = false
  }, props.duration || 3000)
}

const hide = () => {
  visible.value = false
  if (timer.value) {
    clearTimeout(timer.value)
    timer.value = null
  }
}

watch(() => props.message, () => {
  if (props.message) {
    show()
  }
})

defineExpose({
  show,
  hide
})
</script>

