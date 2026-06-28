<script setup lang="ts">
import { ApiReference } from "@scalar/api-reference";
import "@scalar/api-reference/style.css";
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { LockClosedIcon } from "@heroicons/vue/24/outline";

const router = useRouter();
const apiKey = localStorage.getItem("api_key") || "";
const specContent = ref<any>(null);
const isLoggedIn = ref(!!apiKey);
const loading = ref(true);
const error = ref("");

onMounted(async () => {
  if (!apiKey) {
    isLoggedIn.value = false;
    loading.value = false;
    return;
  }

  try {
    const response = await fetch("/openapi.json");

    // Handle auth errors from the fetch itself (if protected)
    if (response.status === 401 || response.status === 403) {
      isLoggedIn.value = false;
      loading.value = false;
      // Optional: Clear invalid key if backend rejeceted it
      localStorage.removeItem("api_key");
      return;
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const spec = await response.json();

    // Filter paths to only include those starting with /api/v1
    const filteredPaths: Record<string, any> = {};
    if (spec.paths) {
      Object.keys(spec.paths).forEach((path) => {
        if (path.startsWith("/api/v1")) {
          filteredPaths[path] = spec.paths[path];
        }
      });
      spec.paths = filteredPaths;
    }

    specContent.value = spec;
  } catch (e: any) {
    console.error("Failed to load or filter openapi.json", e);
    error.value = "无法加载 API 定义: " + (e.message || "Unknown error");
  } finally {
    loading.value = false;
  }
});

const configuration = computed(
  () =>
    ({
      spec: {
        content: specContent.value,
      },
      authentication: {
        preferredSecurityScheme: "APIKeyHeader",
        apiKey: {
          token: apiKey,
        },
      },
      theme: "purple",
      hideDownloadButton: true,
    } as const)
);
</script>

<template>
  <div class="bg-white rounded-lg shadow min-h-full">
    <div
      v-if="!isLoggedIn"
      class="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6"
    >
      <div class="bg-blue-50 p-6 rounded-full">
        <LockClosedIcon class="w-12 h-12 text-blue-500" />
      </div>
      <h3 class="text-xl font-semibold text-gray-900">需要登录</h3>
      <p class="text-gray-500 max-w-sm">
        您需要登录后才能访问 API Playground 调试接口。
      </p>
      <button
        @click="router.push('/login')"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      >
        立即登录
      </button>
    </div>
    <div
      v-else-if="loading"
      class="p-8 text-center text-gray-500 flex flex-col items-center justify-center min-h-[40vh]"
    >
      <div
        class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mb-4"
      ></div>
      Loading API Definition...
    </div>
    <div v-else-if="error" class="p-8 text-center text-red-500">
      {{ error }}
    </div>
    <ApiReference v-else :configuration="configuration" />
  </div>
</template>

<style scoped>
/* Removed h-full and overflow-hidden to allow natural scrolling within the dashboard content area */

/* Localization Overrides */

/* "Test Request" Button */
:deep(.show-api-client-button span) {
  font-size: 0 !important;
}
:deep(.show-api-client-button span::after) {
  content: "调试接口";
  font-size: 14px;
}

/* "Body" Header */
:deep(.request-body-title) {
  font-size: 0 !important;
}
:deep(.request-body-title::after) {
  content: "请求体";
  font-size: 13px;
  font-weight: 500;
}

/* Generic Headers (Responses, Parameters) - This is tricky as classes are generic */
/* Attempting to target via text content is impossible directly in CSS. */
/* We will target specific containers where we know the order or structure */

/* Responses Header often has specific classes */
/* .text-c-1.mt-3.mb-3.leading-\[1\.45\].font-medium */
/* Since we can't be precise without unique classes, we will skip riskier generic overrides */
/* But "Operation" title sections might be targetable */

:deep(.scalar-card-header-title) {
  font-size: 0 !important;
}
:deep(.scalar-card-header-title::after) {
  content: "接口定义"; /* Or 'Operations' translated */
  font-size: 1rem;
}
</style>
