<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  text: string
  position?: 'top' | 'bottom' | 'left' | 'right'
  align?: 'start' | 'center' | 'end'
}>()

const show = ref(false)
</script>

<template>
  <div class="relative inline-block" @mouseenter="show = true" @mouseleave="show = false">
    <slot></slot>
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 translate-y-1"
    >
      <div v-if="show" 
        :class="[
          'absolute z-[9999] px-2 py-1.5 text-xs font-medium text-white bg-gray-900 rounded-lg shadow-xl whitespace-nowrap pointer-events-none',
          // Position Top
          (position === 'top' || !position) ? 'bottom-full mb-2' : '',
          (position === 'top' || !position) && (align === 'center' || !align) ? 'left-1/2 -translate-x-1/2' : '',
          (position === 'top' || !position) && align === 'start' ? 'left-0' : '',
          (position === 'top' || !position) && align === 'end' ? 'right-0' : '',

          // Position Bottom
          position === 'bottom' ? 'top-full mt-2' : '',
          position === 'bottom' && (align === 'center' || !align) ? 'left-1/2 -translate-x-1/2' : '',
          position === 'bottom' && align === 'start' ? 'left-0' : '',
          position === 'bottom' && align === 'end' ? 'right-0' : '',

          // Position Left/Right (Center align by default)
          position === 'left' ? 'right-full top-1/2 -translate-y-1/2 mr-2' : '',
          position === 'right' ? 'left-full top-1/2 -translate-y-1/2 ml-2' : '',
        ]"
      >
        {{ text }}
        <!-- Triangle Arrow -->
        <div v-if="align === 'center' || !align"
          :class="[
            'absolute w-2 h-2 bg-gray-900 transform rotate-45',
            (position === 'top' || !position) ? 'bottom-[-4px] left-1/2 -translate-x-1/2' : '',
            position === 'bottom' ? 'top-[-4px] left-1/2 -translate-x-1/2' : '',
            position === 'left' ? 'right-[-4px] top-1/2 -translate-y-1/2' : '',
            position === 'right' ? 'left-[-4px] top-1/2 -translate-y-1/2' : ''
          ]"
        ></div>
      </div>
    </transition>
  </div>
</template>
