/**
 * 项目统一配置文件
 * 从环境变量中读取配置
 */

// API服务基础URL
const DEFAULT_API_URL = 'http://localhost:20201'
let apiBaseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_URL

// 强制替换8080端口为20201（如果环境变量错误设置了8080）
if (apiBaseUrl.includes(':8080')) {
  console.warn('[Config] 检测到8080端口，已自动替换为20201')
  apiBaseUrl = apiBaseUrl.replace(':8080', ':20201')
}

export const API_BASE_URL = apiBaseUrl

// 开发环境调试：打印当前使用的 API 地址
if (import.meta.env.DEV) {
  console.log('[Config] API_BASE_URL:', API_BASE_URL)
  console.log('[Config] VITE_API_BASE_URL env:', import.meta.env.VITE_API_BASE_URL)
}

