import type { RouteLocationRaw } from 'vue-router'

/**
 * Scalar ApiReference tag slug（与 Scalar 默认 cRe 行为一致：小写、去标点、空格转连字符）。
 */
export function scalarTagSlug(name: string): string {
  if (!name) return ''
  return name
    .toLowerCase()
    .replace(/[\0-\x1F!-,\.\/:-@\[-\^`{|}~\u200B-\u200F\u202A-\u202E\uFEFF]/g, '')
    .replace(/\s+/g, '-')
}

/** Scalar 操作深链 hash，例如 #tag/xl/GET/api/v1/resources/test001 */
export function buildPlaygroundOperationHash(
  resourceKey: string,
  resourceGroup?: string | null
): string {
  const tag = scalarTagSlug(resourceGroup?.trim() || '默认分组')
  return `#tag/${tag}/GET/api/v1/resources/${resourceKey}`
}

export function buildPlaygroundRoute(resource: {
  resource_key: string
  resource_group?: string | null
}): RouteLocationRaw {
  const group = resource.resource_group?.trim() || undefined
  return {
    path: '/dashboard/playground',
    query: {
      resource: resource.resource_key,
      ...(group ? { group } : {}),
    },
    hash: buildPlaygroundOperationHash(resource.resource_key, group),
  }
}
