import { createApp } from 'vue'
import './style.css'
import App from '@/App.vue'
import router from '@/router'
import { loadBranding } from '@/composables/useBranding'

// 初始化 axios 拦截器（401 统一处理）
import '@/utils/axios'

loadBranding()

const app = createApp(App)
app.use(router)
app.mount('#app')
