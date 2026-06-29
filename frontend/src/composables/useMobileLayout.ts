import { ref, computed, onMounted, onUnmounted } from 'vue'

export const MOBILE_LAYOUT_BREAKPOINT = 1024

export function useMobileLayout() {
  const windowWidth = ref(
    typeof window !== 'undefined' ? window.innerWidth : MOBILE_LAYOUT_BREAKPOINT,
  )
  const isMobile = computed(() => windowWidth.value < MOBILE_LAYOUT_BREAKPOINT)
  const showMobileSidebar = ref(false)

  const handleResize = () => {
    windowWidth.value = window.innerWidth
    if (!isMobile.value) {
      showMobileSidebar.value = false
    }
  }

  onMounted(() => {
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })

  const toggleMobileSidebar = () => {
    showMobileSidebar.value = !showMobileSidebar.value
  }

  const closeMobileSidebar = () => {
    showMobileSidebar.value = false
  }

  return {
    isMobile,
    showMobileSidebar,
    toggleMobileSidebar,
    closeMobileSidebar,
  }
}
