<script setup>
import { ElUpload, ElIcon, ElMessage, ElRadioGroup, ElRadioButton, ElInput, ElInputNumber, ElCollapse, ElCollapseItem, ElTooltip } from 'element-plus'
import { UploadFilled, VideoCamera, Promotion, RefreshRight, Loading, Setting } from '@element-plus/icons-vue'
import { ref, watch } from 'vue'
import RemarksInput from '../common/RemarksInput.vue'

const props = defineProps({
  ffmpegLoading: {
    type: Boolean,
    default: false
  },
  isProcessing: {
    type: Boolean,
    default: false
  },
  acceptHint: {
    type: String,
    default: '上传视频或Mp3音频'
  },
  file: Object,
  fileName: String,
  fileSize: Number,
  fileMd5: String,
  style: String,
  showStyleSelector: Boolean,
  disabled: Boolean,
  md5Calculating: {
    type: Boolean,
    default: false
  },
  remarks: {
    type: String,
    default: ''
  },
  timeout: {
    type: Number,
    default: 120
  },
  maxTokens: {
    type: Number,
    default: 8192
  }
})

const emit = defineEmits(['file-selected', 'update:style', 'update:remarks', 'update:timeout', 'update:maxTokens', 'start-process', 'reset'])

const allowedTypes = [
  'video/mp4',
  'video/quicktime',
  'video/x-msvideo',
  'video/x-matroska',
  'video/webm',
  'audio/mpeg'
]

// 获取本地设置的最大上传文件大小（单位MB），默认200
function getLocalMaxUploadSize() {
  try {
    const v = localStorage.getItem('maxUploadSize')
    if (v) {
      const n = parseInt(v)
      if (!isNaN(n) && n >= 10) return n
    }
  } catch { }
  return 200
}

const handleFileChange = (file) => {
  const isAllowedType = allowedTypes.includes(file.raw.type) ||
    file.raw.name.toLowerCase().endsWith('.mp3');
  if (!isAllowedType) {
    ElMessage.error('只支持上传视频文件（MP4、MOV、AVI、MKV、WebM）或MP3音频文件')
    return false
  }
  const maxSize = getLocalMaxUploadSize() * 1024 * 1024
  if (file.raw.size > maxSize) {
    ElMessage.error(`文件大小不能超过 ${getLocalMaxUploadSize()}MB`)
    return false
  }
  emit('file-selected', file.raw)
}

// 支持风格类型及图标
const styleList = [
  { label: 'note', name: '知识笔记', icon: new URL('../../assets/笔记.svg', import.meta.url).href },
  { label: 'xiaohongshu', name: '小红书', icon: new URL('../../assets/小红书.svg', import.meta.url).href },
  { label: 'wechat', name: '公众号', icon: new URL('../../assets/微信公众号.svg', import.meta.url).href },
  { label: 'summary', name: '内容总结', icon: new URL('../../assets/汇总.svg', import.meta.url).href },
]

const localStyle = ref(props.style || '')
watch(() => props.style, v => { localStyle.value = v })
const handleStyleChange = (val) => {
  emit('update:style', val)
}
const handleStart = () => {
  emit('start-process')
}
const handleReset = () => {
  emit('reset')
}

const localRemarks = ref(props.remarks || '')
const localTimeout = ref(props.timeout)
const localMaxTokens = ref(props.maxTokens)

watch(() => props.remarks, v => { localRemarks.value = v })
watch(() => props.timeout, v => { localTimeout.value = v })
watch(() => props.maxTokens, v => { localMaxTokens.value = v })

const handleRemarksChange = (val) => {
  emit('update:remarks', val)
}

const handleTimeoutChange = (val) => {
  emit('update:timeout', val)
}

const handleMaxTokensChange = (val) => {
  emit('update:maxTokens', val)
}
</script>

<template>
  <div class="upload-section-outer">
    <div class="upload-section" :class="{ 'loading-state': ffmpegLoading }">
      <div class="welcome">
        <div class="welcome-title">你好，我是 <span class="ai-highlight">智梦AI</span></div>
        <div class="welcome-desc">
          <p class="desc-line">上传你的视频或MP3音频，我会帮你自动转写并生成多种风格的图文内容。</p>
          <p class="desc-line">✨ 智能识别：支持多种视频和音频格式，自动提取音轨并转写为文字</p>
          <p class="desc-line">📝 多风格输出：支持知识笔记、小红书、公众号、内容总结等多种风格</p>
          <p class="desc-line">🎯 精准处理：基于AI大模型，智能理解内容并生成高质量文档</p>
          <p class="desc-line">⚡ 快速高效：一键处理，无需复杂操作，轻松完成音视频转文档</p>
        </div>
      </div>
      <!-- 仅在未上传文件时显示风格支持列表和acceptHint -->
      <div v-if="!props.file">
        <div class="style-support-list">
          <div class="style-support-item" v-for="item in styleList" :key="item.label">
            <img :src="item.icon" :alt="item.name" class="style-support-icon" />
            <span class="style-support-name">{{ item.name }}</span>
          </div>
        </div>
        <h3 class="section-title">
          <el-icon>
            <VideoCamera />
          </el-icon>
          {{ acceptHint }}
        </h3>
      </div>
      <!-- 上传区域：仅在未上传文件时显示 -->
      <el-upload v-if="!props.file" class="uploader" drag action="" :auto-upload="false" :on-change="handleFileChange"
        :disabled="ffmpegLoading || isProcessing" :accept="allowedTypes.join(',') + ',.mp3'">
        <div class="upload-content">
          <div class="upload-icon-wrapper">
            <el-icon class="upload-icon">
              <UploadFilled />
            </el-icon>
          </div>
          <h3 class="upload-title">
            {{ ffmpegLoading ? '正在加载 ffmpeg，请稍候...' : '开始上传' }}
          </h3>
          <p class="upload-desc" v-if="!ffmpegLoading">
            支持拖放或点击上传视频或MP3文件<br>
            <span class="upload-formats">支持格式：MP4、MOV、AVI、MKV、WebM、MP3，当前设置最大值为 {{ getLocalMaxUploadSize() }}MB</span>
            <el-tooltip content="可以在自定义设置中调整大小。" placement="top" effect="dark">
              <span class="size-tip-hint">?</span>
            </el-tooltip>
          </p>
        </div>
      </el-upload>
      <!-- 文件信息和风格选择：上传后显示 -->
      <div v-else class="file-info-section">
        <div class="file-info-card">
          <div class="file-info-row">
            <span class="file-info-label">文件名：</span>
            <span class="file-info-value">{{ props.fileName }}</span>
          </div>
          <div class="file-info-row">
            <span class="file-info-label">文件大小：</span>
            <span class="file-info-value">{{ (props.fileSize / 1024 / 1024).toFixed(2) }} MB</span>
          </div>
          <div class="file-info-row">
            <span class="file-info-label">文件MD5：</span>
            <span class="file-info-value file-info-md5">
              <template v-if="props.md5Calculating">
                <el-icon class="md5-loading-icon">
                  <Loading />
                </el-icon>
                正在计算 MD5
                <span class="md5-loading-dots">
                  <span>.</span><span>.</span><span>.</span>
                </span>
              </template>
              <template v-else>
                {{ props.fileMd5 }}
              </template>
            </span>
          </div>
        </div>
        <div class="file-info-main">
          <div class="style-selector-wrapper style-selector-flex">
            <el-radio-group v-model="localStyle" :disabled="isProcessing" @change="handleStyleChange" size="large"
              class="style-radio-group-flex">
              <el-radio-button v-for="item in styleList" :key="item.label" :label="item.label"
                class="style-radio-btn-flex">
                <img :src="item.icon" :alt="item.name" class="style-radio-icon" />
                {{ item.name }}
              </el-radio-button>
            </el-radio-group>
          </div>
          <RemarksInput v-model="localRemarks" :timeout="localTimeout" :max-tokens="localMaxTokens"
            :disabled="isProcessing" @update:modelValue="handleRemarksChange" @update:timeout="handleTimeoutChange"
            @update:maxTokens="handleMaxTokensChange" placeholder="你可以添加备注在默认提示词的基础上实现更加个性化的输出, 例如: 输出更详细一些" />
        </div>
        <div class="file-action-row">
          <el-button class="start-process-btn" :disabled="!localStyle || isProcessing" @click="handleStart">
            <el-icon class="plane-icon">
              <Promotion />
            </el-icon>
            开始处理
          </el-button>
        </div>
        <!-- 右下角悬浮的重新选择文件按钮 -->
        <a href="#" @click.prevent="handleReset" class="reset-link-float upload-section-reset-link">
          <el-icon class="reset-icon">
            <RefreshRight />
          </el-icon>
          重新选择文件
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-section-outer {
  min-height: 70vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  width: 100%;
  box-sizing: border-box;
  background: transparent;
  /* margin-top: 12vh; */
}

.upload-section {
  width: 60vw;
  max-width: 900px;
  min-width: 340px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.9) 100%);
  border-radius: 24px;
  padding: 2.8rem 2.2rem 2.2rem 2.2rem;
  border: none;
  box-sizing: border-box;
  margin: 0;
  height: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #e2e8f0;
  position: relative;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.5), 0 2px 12px rgba(99, 102, 241, 0.3);
  border: 1px solid rgba(99, 102, 241, 0.3);
  transition: all 0.3s ease;
}

.upload-section:hover {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6), 0 4px 16px rgba(99, 102, 241, 0.4);
  border-color: rgba(129, 140, 248, 0.5);
}

.welcome {
  width: 100%;
  text-align: center;
  margin-bottom: 1.8rem;
}

.welcome-title {
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: 0.5px;
  margin-bottom: 0.8rem;
  color: #ffffff;
  line-height: 1.3;
}

.ai-highlight {
  background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 900;
  letter-spacing: 0.5px;
  position: relative;
  text-shadow: 0 0 20px rgba(129, 140, 248, 0.3);
}

.welcome-desc {
  font-size: 1rem;
  color: #94a3b8;
  margin-bottom: 0.2rem;
  font-weight: 400;
  line-height: 1.8;
  text-align: left;
}

.welcome-desc .desc-line {
  margin: 0.5rem 0;
  font-size: 0.95rem;
  color: #cbd5e1;
  line-height: 1.8;
}

.welcome-desc .desc-line:first-child {
  margin-top: 0;
  font-size: 1.05rem;
  color: #e2e8f0;
  font-weight: 500;
}

.style-support-list {
  width: 100%;
  display: flex;
  justify-content: center;
  gap: 18px;
  margin-bottom: 1.6rem;
  margin-top: -0.5rem;
  flex-wrap: wrap;
}

.style-support-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 16px;
  padding: 0.7rem 1.1rem 0.5rem 1.1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(99, 102, 241, 0.3);
  min-width: 80px;
  min-height: 80px;
  transition: all 0.3s ease;
}

.style-support-item:hover {
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
  border-color: rgba(129, 140, 248, 0.5);
  transform: translateY(-2px);
  background: rgba(99, 102, 241, 0.2);
}

.style-support-icon {
  width: 32px;
  height: 32px;
  margin-bottom: 0.5rem;
  user-drag: none;
  user-select: none;
}

.style-support-name {
  font-size: 0.98rem;
  color: #e2e8f0;
  font-weight: 600;
  letter-spacing: 0.1px;
}

.section-title {
  font-size: 1.15rem;
  color: #ffffff;
  margin-bottom: 0.8rem;
  font-weight: 700;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: 0.2px;
}

.section-title .el-icon {
  font-size: 1.3rem;
  color: #818cf8;
  background: rgba(99, 102, 241, 0.3);
  border-radius: 50%;
  padding: 6px;
}

.uploader {
  width: 100%;
}

.uploader :deep(.el-upload) {
  border: 2px dashed rgba(129, 140, 248, 0.4) !important;
  border-radius: 16px !important;
  background: rgba(15, 23, 42, 0.4) !important;
  transition: all 0.3s ease;
}

.uploader :deep(.el-upload:hover) {
  border-color: rgba(129, 140, 248, 0.7) !important;
  background: rgba(99, 102, 241, 0.15) !important;
}

.upload-content {
  text-align: center;
  padding: 1.2rem 0.5rem 0.5rem 0.5rem;
}

.upload-icon-wrapper {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 50%;
  margin: 0 auto 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
  transition: all 0.3s ease;
}

.upload-icon-wrapper:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 24px rgba(99, 102, 241, 0.4);
}

.upload-icon {
  font-size: 2.2rem;
  color: #ffffff;
}

.upload-title {
  font-size: 1.2rem;
  color: #ffffff;
  margin: 0.5rem 0;
  font-weight: 700;
  letter-spacing: 0.2px;
}

.upload-desc {
  color: #94a3b8;
  line-height: 1.6;
  font-size: 1.01rem;
  margin-top: 0.2rem;
}

.upload-formats {
  font-size: 0.93rem;
  color: #cbd5e1;
  font-weight: 500;
  letter-spacing: 0.1px;
}

.size-tip-hint {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-left: 6px;
  border-radius: 50%;
  background: #f3f4f6;
  color: #6b7280;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #e5e7eb;
  cursor: help;
}

.loading-state {
  background-color: #f7f7fa !important;
  pointer-events: none;
  opacity: 0.8;
}

/* 文件信息和风格选择样式 */
.file-info-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.0rem;
  background: transparent;
  box-shadow: none;
  border: none;
}

.file-info-main {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* 不设置gap，间距用margin控制 */
}

.file-info-card {
  width: 93%;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 16px;
  padding: 1.5rem 2rem 1.2rem 2rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(99, 102, 241, 0.3);
  margin-bottom: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.file-info-row {
  display: grid;
  grid-template-columns: 90px 1fr;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.03rem;
  color: #23272f;
  font-weight: 500;
  word-break: break-all;
  padding: 0.1rem 0;
}

.file-info-label {
  color: #94a3b8;
  font-size: 1.01rem;
  font-weight: 500;
  min-width: 70px;
  width: 90px;
  text-align: right;
  justify-self: end;
  /* 右对齐标签 */
}

.file-info-value {
  color: #e2e8f0;
  font-size: 1.03rem;
  font-weight: 600;
  word-break: break-all;
  text-align: left;
  justify-self: start;
}

.file-info-md5 {
  font-family: monospace;
  font-size: 0.98rem;
  color: #888;
  background: #f3f4f6;
  border-radius: 4px;
  padding: 2px 6px;
  word-break: break-all;
  display: flex;
  align-items: center;
  gap: 6px;
}

.md5-loading-icon {
  font-size: 1.1em;
  color: #888;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

.md5-loading-dots span {
  animation: blink 1.4s infinite both;
  opacity: 0.5;
  font-size: 1.2em;
}

.md5-loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.md5-loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {

  0%,
  80%,
  100% {
    opacity: 0.5;
  }

  40% {
    opacity: 1;
  }
}

.style-selector-wrapper {
  margin-top: 0;
  margin-bottom: 0.6rem;
  /* 控制与下方remarks的间距 */
}

.start-process-btn {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 12px !important;
  font-size: 1.1rem;
  font-weight: 700;
  padding: 0.8rem 2.4rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
}

.start-process-btn:disabled {
  background: #e5e7eb !important;
  color: #b0b3b8 !important;
  cursor: not-allowed !important;
  box-shadow: none;
}

.start-process-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
  box-shadow: 0 6px 24px rgba(99, 102, 241, 0.4);
  transform: translateY(-1px);
}


.style-selector-flex {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
  align-items: center;
  gap: 0.5rem 0.5rem;
  /* 允许内容自动换行 */
  overflow-x: auto;
}

.style-radio-group-flex {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 0.5rem 0.5rem;
  width: 100%;
}

.style-radio-btn-flex {
  margin-right: 0 !important;
  margin-bottom: 0 !important;
  flex: 0 1 auto;
  min-width: 110px;
  max-width: 180px;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.file-action-row {
  width: 100%;
  max-width: 520px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.2rem;
  margin-top: 0.5rem;
  position: relative;
}

/* 右下角悬浮的重新选择文件按钮 */
.upload-section-reset-link {
  position: absolute;
  right: 0.5rem;
  bottom: 0.5rem;
  color: #94a3b8;
  font-size: 0.95rem;
  text-decoration: none;
  cursor: pointer;
  background: #fff;
  border-radius: 10px;
  padding: 4px 12px 4px 8px;
  transition: all 0.3s ease;
  z-index: 2;
  opacity: 0.9;
  display: flex;
  align-items: center;
  gap: 4px;
  border: 1px solid rgba(226, 232, 240, 0.8);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.upload-section-reset-link:hover {
  color: #6366f1;
  border-color: rgba(99, 102, 241, 0.3);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  transform: translateY(-1px);
}

.reset-icon {
  font-size: 1.1em;
  margin-right: 2px;
  vertical-align: middle;
}

/* 隐藏方框内的reset-link-inside和reset-link */
.reset-link-inside,
.reset-link {
  display: none !important;
}

/* 已在 .uploader :deep(.el-upload) 中定义，此处删除重复样式 */

:deep(.el-upload-dragger) {
  background: transparent !important;
  color: #23272f !important;
}

:deep(.el-upload-list) {
  color: #23272f !important;
}

:deep(.el-radio-button__inner) {
  border: 1px solid #dcdfe6;
  border-radius: 8px !important;
}

.style-radio-icon {
  width: 20px;
  height: 20px;
  margin-right: 6px;
  vertical-align: middle;
}

@media screen and (max-width: 900px) {
  .upload-section {
    width: 98vw;
    max-width: 98vw;
    padding: 1.2rem 0.5rem;
    border-radius: 14px;
  }

  .upload-section-outer {
    min-height: 60vh;
    margin-top: 3vh;
  }

  .welcome-title {
    font-size: 1.13rem;
  }

  .style-support-list {
    gap: 10px;
    margin-bottom: 1.1rem;
  }

  .style-support-item {
    min-width: 64px;
    min-height: 64px;
    padding: 0.5rem 0.7rem 0.4rem 0.7rem;
  }

  .style-support-icon {
    width: 24px;
    height: 24px;
  }
}

.remarks-wrapper {
  width: 93%;
  margin-bottom: 0.5rem;
  margin-top: 0;
  /* 可根据需要调整与上方的距离 */
}

.remarks-input {
  width: 100%;
}

:deep(.remarks-input .el-textarea__inner) {
  background: #f7f8fa !important;
  border: 1.5px solid #f2f3f5 !important;
  border-radius: 14px !important;
  padding: 16px 20px !important;
  font-size: 1.01rem !important;
  color: #23272f !important;
  transition: border-color 0.18s, box-shadow 0.18s !important;
  resize: none !important;
  font-family: inherit !important;
  line-height: 1.5 !important;
  box-shadow: 0 2px 10px 0 rgba(60, 80, 120, 0.04) !important;
}

:deep(.remarks-input .el-textarea__inner:focus) {
  border-color: #23272f !important;
  box-shadow: 0 0 0 2px rgba(35, 39, 47, 0.1), 0 2px 10px 0 rgba(60, 80, 120, 0.04) !important;
  outline: none !important;
}

:deep(.remarks-input .el-textarea__inner::placeholder) {
  color: #9ca3af !important;
  font-size: 0.98rem !important;
  line-height: 1.5 !important;
}

:deep(.remarks-input .el-textarea__inner:disabled) {
  background: #f3f4f6 !important;
  color: #9ca3af !important;
  cursor: not-allowed !important;
  border-color: #e5e7eb !important;
}
</style>
