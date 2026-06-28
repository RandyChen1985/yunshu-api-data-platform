<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

const props = defineProps<{
  direction: 'horizontal' | 'vertical'
  min?: number
  max?: number
}>()

const emit = defineEmits<{
  (e: 'resize', size: number): void
}>()

const isResizing = ref(false)

const startResizing = () => {
  isResizing.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', stopResizing)
  document.body.style.cursor = props.direction === 'horizontal' ? 'col-resize' : 'row-resize'
  document.body.style.userSelect = 'none'
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isResizing.value) return
  
  let newSize: number
  if (props.direction === 'horizontal') {
    newSize = e.clientX
  } else {
    // For vertical, we often want the height from the top or distance from a reference
    // We'll emit the raw position and let the parent handle the delta/absolute calc
    newSize = e.clientY
  }
  
  emit('resize', newSize)
}

const stopResizing = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', stopResizing)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

onUnmounted(stopResizing)
</script>

<template>
  <div 
    class="resize-handle transition-colors duration-200"
    :class="[
      direction === 'horizontal' ? 'w-1 cursor-col-resize hover:bg-blue-500' : 'h-1 cursor-row-resize hover:bg-blue-500',
      isResizing ? 'bg-blue-600' : 'bg-transparent'
    ]"
    @mousedown="startResizing"
  ></div>
</template>

<style scoped>
.resize-handle {
  flex-shrink: 0;
  z-index: 10;
}
</style>
