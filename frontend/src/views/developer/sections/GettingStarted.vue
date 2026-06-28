<template>
  <div class="prose max-w-none">
    <section>
      <h2 class="text-xl font-semibold mb-4 text-gray-800">1. 获取凭证 (API Key)</h2>
      <p>在开始调用 API 之前，您需要获取一个有效的 API Key：</p>
      <ol class="list-decimal pl-5 space-y-2">
        <li>登录管理后台。</li>
        <li>进入 <strong>“个人中心”</strong> 或 <strong>“我的密钥”</strong>。</li>
        <li>点击 <strong>“生成新密钥”</strong>。请妥善保管您的密钥，系统不会再次展示。</li>
      </ol>
      <div class="bg-blue-50 border-l-4 border-blue-400 p-4 my-4">
        <p class="text-sm text-blue-700 font-medium">安全提示：API Key 拥有您的账户访问权限，切勿将其硬编码在前端页面或公开的代码仓库中。</p>
      </div>
    </section>

    <section class="mt-10">
      <h2 class="text-xl font-semibold mb-4 text-gray-800">2. 发起第一个请求 (cURL)</h2>
      <p class="mb-2"><strong>API 服务地址：</strong> <code class="bg-gray-100 px-2 py-1 rounded text-sm text-blue-600">https://your-api-host.example.com</code></p>
      <p class="mb-4">使用 cURL 测试您的密钥是否有效（请将地址替换为实际部署的 API 域名）：</p>
      <pre class="bg-gray-900 text-white p-4 rounded-lg overflow-x-auto"><code>curl -X GET "https://your-api-host.example.com/api/v1/resources/rooms" \
  -H "X-API-Key: YOUR_API_KEY_HERE"</code></pre>
    </section>

    <section class="mt-10">
      <h2 class="text-xl font-semibold mb-4 text-gray-800">3. 响应结构</h2>
      <p>所有接口均返回统一的 Envelope 结构：</p>
      <pre class="bg-gray-100 p-4 rounded-lg"><code>{
  "code": 200,          // 业务错误码 (200 代表成功)
  "message": "success", // 提示信息
  "data": { ... },      // 业务负载
  "trace_id": "...",    // 链路追踪 ID
  "timestamp": "..."    // 服务端时间戳
}</code></pre>
    </section>
  </div>
</template>
