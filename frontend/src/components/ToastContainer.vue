<template>
  <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
    <TransitionGroup
      enter-active-class="transition ease-out duration-300"
      enter-from-class="transform translate-x-full opacity-0"
      enter-to-class="transform translate-x-0 opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="transform translate-x-0 opacity-100"
      leave-to-class="transform translate-x-full opacity-0"
    >
      <Toast 
        v-for="toast in toasts" 
        :key="toast.id"
        :message="toast.message" 
        :type="toast.type"
        :duration="toast.duration"
        @close="removeToast(toast.id)"
        class="pointer-events-auto"
      />
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useToast } from '../composables/useToast'
import Toast from './Toast.vue'

const { toasts, removeToast } = useToast()
</script>
