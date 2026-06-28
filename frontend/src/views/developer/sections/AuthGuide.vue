<template>
  <div class="prose max-w-none">
    <h2 class="text-xl font-semibold mb-4 text-gray-800">认证与鉴权详解</h2>
    <p>平台采用基于 <strong>API Key</strong> 的鉴权方案。所有受保护的 API 接口都必须在请求头中携带有效的凭证。</p>

    <h3 class="text-lg font-medium mt-6 mb-2">1. 请求头格式</h3>
    <table class="min-w-full border text-sm">
      <thead class="bg-gray-50">
        <tr>
          <th class="border px-4 py-2 text-left">Header Name</th>
          <th class="border px-4 py-2 text-left">Value</th>
          <th class="border px-4 py-2 text-left">说明</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="border px-4 py-2 font-mono">X-API-Key</td>
          <td class="border px-4 py-2 font-mono">yovole_sk_...</td>
          <td class="border px-4 py-2">您的私有密钥 (必填)</td>
        </tr>
        <tr>
          <td class="border px-4 py-2 font-mono">Content-Type</td>
          <td class="border px-4 py-2 font-mono">application/json</td>
          <td class="border px-4 py-2">数据交互格式 (建议)</td>
        </tr>
      </tbody>
    </table>

    <h3 class="text-lg font-medium mt-8 mb-2">2. 权限级别说明</h3>
    <ul class="list-disc pl-5 space-y-2">
      <li><strong>Admin 权限</strong>：可以访问所有管理类接口（用户管理、密钥管理、系统审计等）。</li>
      <li><strong>User 权限</strong>：仅能访问资源查询接口（Resources API）和个人审计日志。</li>
    </ul>

    <h3 class="text-lg font-medium mt-8 mb-2">3. 速率限制 (Rate Limiting)</h3>
    <p>为了保障系统稳定性，每个 API Key 的并发请求受到限制。当触发限制时，系统将返回 <code>429 Too Many Requests</code> 错误。</p>
  </div>
</template>
