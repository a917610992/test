import axios, { AxiosRequestConfig, AxiosResponse, AxiosInstance } from 'axios'
import { ElMessage } from 'element-plus'
import { API_BASE_URL } from '../config'
import { APIResponse } from './types'

/**
 * 统一的API请求错误
 */
export class ApiError extends Error {
  status: number
  data?: any

  constructor(message: string, status: number = 500, data?: any) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

/**
 * 统一的HTTP请求服务
 */
class HttpService {
  private axiosInstance: AxiosInstance

  constructor(baseURL: string) {
    console.log('HttpService initialized with baseURL:', baseURL)
    this.axiosInstance = axios.create({
      baseURL,
      timeout: 240000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    // 请求拦截器
    this.axiosInstance.interceptors.request.use(
      config => {
        // 对于 FormData，移除 Content-Type 让浏览器自动设置（必须在添加其他头部之前）
        if (config.data instanceof FormData) {
          delete config.headers['Content-Type']
        }
        
        // 调试：打印请求URL
        const fullUrl = config.baseURL ? `${config.baseURL}${config.url || ''}` : (config.url || '')
        console.log('[HTTP Request]', config.method?.toUpperCase(), fullUrl, config.data instanceof FormData ? '(FormData)' : '')
        
        // 自动添加Web访问密码请求头
        try {
          const webAccessPassword = localStorage.getItem('webAccessPassword')
          if (webAccessPassword) {
            config.headers = config.headers || {}
            config.headers['request-web-access-password'] = webAccessPassword
          }
        } catch (error) {
          console.warn('获取Web访问密码失败:', error)
        }

        // 自动添加模型配置请求头
        try {
          const llmConfig = localStorage.getItem('llmConfig')
          const storageConfig = localStorage.getItem('storageConfig')
          const asrConfig = localStorage.getItem('asrConfig')
          
          config.headers = config.headers || {}
          
          if (llmConfig) {
            const llm = JSON.parse(llmConfig)
            if (llm.baseUrl) config.headers['x-llm-base-url'] = llm.baseUrl
            if (llm.modelId) config.headers['x-llm-model-id'] = llm.modelId
            if (llm.apiKey) config.headers['x-llm-api-key'] = llm.apiKey
          }
          
          if (storageConfig) {
            const storage = JSON.parse(storageConfig)
            if (storage.accessKey) config.headers['x-storage-access-key'] = storage.accessKey
            if (storage.secretKey) config.headers['x-storage-secret-key'] = storage.secretKey
            if (storage.endpoint) config.headers['x-storage-endpoint'] = storage.endpoint
            if (storage.region) config.headers['x-storage-region'] = storage.region
            if (storage.bucket) config.headers['x-storage-bucket'] = storage.bucket
          }
          
          if (asrConfig) {
            const asr = JSON.parse(asrConfig)
            if (asr.appId) config.headers['x-asr-app-id'] = asr.appId
            if (asr.accessToken) config.headers['x-asr-access-token'] = asr.accessToken
            if (asr.clusterId) config.headers['x-asr-cluster-id'] = asr.clusterId
          }
        } catch (error) {
          console.warn('获取模型配置失败:', error)
        }
        
        return config
      },
      error => Promise.reject(error)
    )

    // 响应拦截器
    this.axiosInstance.interceptors.response.use(
      response => {
        const data = response.data as APIResponse
        
        // 检查业务逻辑是否成功
        if (data && typeof data === 'object' && 'success' in data && !data.success) {
          const message = data.error?.message || '请求失败'
          console.error('API业务错误:', message, data.error)
          ElMessage.error(message)
          throw new ApiError(message, response.status, data)
        }
        
        return data
      },
      error => {
        let message = '请求失败'
        let status = 500
        let data = null
        
        if (error.response) {
          // 服务器返回了错误响应
          status = error.response.status
          data = error.response.data
          
          // 从新的错误格式中提取消息
          if (data && typeof data === 'object') {
            if ('error' in data && (data as any).error?.message) {
              message = (data as any).error.message
            } else if ('detail' in data) {
              message = (data as any).detail
            } else if ('message' in data) {
              message = (data as any).message
            } else {
              message = error.message || '请求失败'
            }
          }
        } else {
          // 网络错误或其他错误
          message = error.message || '网络错误'
        }
        
        console.error(`API错误 [${status}]:`, message, data)
        ElMessage.error(message)
        
        return Promise.reject(new ApiError(message, status, data))
      }
    )
  }

  /**
   * 发送HTTP请求
   * @param config 请求配置
   * @returns 响应数据
   */
  async request<T = any>(config: AxiosRequestConfig): Promise<T> {
    try {
      return await this.axiosInstance.request(config)
    } catch (error) {
      if (error instanceof ApiError) {
        throw error
      }
      throw new ApiError(error.message || '请求失败')
    }
  }

  /**
   * 上传文件（使用XHR以支持进度回调）
   * @param url 上传URL
   * @param file 文件对象
   * @param onProgress 进度回调
   */
  async uploadFile(url: string, file: Blob, onProgress?: (percent: number) => void): Promise<any> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable && onProgress) {
          const percent = Math.round((event.loaded / event.total) * 100)
          onProgress(percent)
        }
      }
      
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve({ success: true, status: xhr.status })
        } else {
          console.error('[Upload Error] Status:', xhr.status, 'Response:', xhr.responseText)
          reject(new ApiError(`上传失败: ${xhr.status} - ${xhr.responseText || xhr.statusText}`, xhr.status))
        }
      }
      
      xhr.onerror = (event) => {
        console.error('[Upload Error] XHR error event:', event)
        console.error('[Upload Error] Status:', xhr.status, 'StatusText:', xhr.statusText)
        console.error('[Upload Error] Response:', xhr.responseText)
        // 如果是 CORS 错误，状态码通常是 0
        if (xhr.status === 0) {
          reject(new ApiError('上传失败: CORS 错误。请检查存储桶的 CORS 配置，确保允许来源、方法和请求头。', 0))
        } else {
          reject(new ApiError(`网络错误，上传失败: ${xhr.statusText || '未知错误'}`, xhr.status || 500))
        }
      }
      
      xhr.onabort = () => {
        reject(new ApiError('上传已取消', 0))
      }
      
      xhr.open('PUT', url)
      // 设置 Content-Type，因为预签名 URL 的签名中包含了 content-type
      // 如果不设置，签名验证会失败
      if (file.type) {
        xhr.setRequestHeader('Content-Type', file.type)
      } else {
        // 如果没有 file.type，根据 URL 中的签名头推断
        // 如果 X-Amz-SignedHeaders 包含 content-type，使用 audio/mpeg 作为默认值
        xhr.setRequestHeader('Content-Type', 'audio/mpeg')
      }
      xhr.send(file)
    })
  }
}

// 导出默认的HTTP服务实例
export default new HttpService(API_BASE_URL)
