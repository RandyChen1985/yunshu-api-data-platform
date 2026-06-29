import { ref, computed, type Ref } from 'vue'

/** 轻量虚拟列表：固定行高场景，无额外依赖 */
export function useSimpleVirtualList<T>(
  items: Ref<T[]>,
  options: { itemHeight: number; containerHeight: number },
) {
  const scrollTop = ref(0)

  const onScroll = (e: Event) => {
    scrollTop.value = (e.target as HTMLElement).scrollTop
  }

  const totalHeight = computed(() => items.value.length * options.itemHeight)

  const startIndex = computed(() =>
    Math.max(0, Math.floor(scrollTop.value / options.itemHeight) - 2),
  )

  const visibleCount = computed(
    () => Math.ceil(options.containerHeight / options.itemHeight) + 4,
  )

  const endIndex = computed(() =>
    Math.min(items.value.length, startIndex.value + visibleCount.value),
  )

  const visibleItems = computed(() =>
    items.value.slice(startIndex.value, endIndex.value),
  )

  const offsetY = computed(() => startIndex.value * options.itemHeight)

  const useVirtual = computed(() => items.value.length >= 20)

  return {
    scrollTop,
    onScroll,
    totalHeight,
    visibleItems,
    offsetY,
    startIndex,
    useVirtual,
  }
}
