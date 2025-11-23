<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import AppSidebar from './components/AppSidebar.vue'
import VideoToMarkdown from './components/VideoToMarkdown/index.vue'
import TaskDetail from './components/VideoToMarkdown/TaskDetail.vue'
import { eventBus } from './utils/eventBus'

const activeMenu = ref('new-task')
const isChatOpen = ref(false)
const selectedTask = ref(null)

const isTaskDetailOpen = ref(false)
const currentTask = ref(null)

const previousMenu = ref('new-task')
const showQRCode = ref(false)
const qrCodeImage = new URL('./image/f83ca226227cbe0b2665c5c2a50e9e26.jpg', import.meta.url).href

const handleMenuSelect = (key) => {
  if (key.startsWith('task-')) {
    const taskId = parseInt(key.replace('task-', ''))
    return;
  }

  isTaskDetailOpen.value = false
  currentTask.value = null
  activeMenu.value = key
}


const handleViewTask = (task) => {
  currentTask.value = task
  isTaskDetailOpen.value = true
  previousMenu.value = activeMenu.value
  activeMenu.value = 'task-detail'
}

onMounted(() => {
  eventBus.on('view-task', handleViewTask)
})
onBeforeUnmount(() => {
  eventBus.off('view-task', handleViewTask)
})
</script>

<template>
  <div class="app-container">
    <AppSidebar :active-menu="activeMenu" @menu-select="handleMenuSelect" @view-task="handleViewTask" />

    <div class="content-area">
      <!-- 右上角联系作者按钮 -->
      <div class="contact-author-container" @mouseenter="showQRCode = true" @mouseleave="showQRCode = false">
        <div class="contact-author-btn">
          联系作者
        </div>
        <!-- 二维码弹出层 -->
        <transition name="fade">
          <div v-if="showQRCode" class="qr-code-popup">
            <img :src="qrCodeImage" alt="微信号二维码" class="qr-code-image" />
          </div>
        </transition>
      </div>

      <div class="content-wrapper">
        <template v-if="isTaskDetailOpen && currentTask">
          <TaskDetail :task="currentTask" />
        </template>
        <template v-else-if="activeMenu === 'new-task'">
          <VideoToMarkdown />
        </template>
        <template v-else>
        </template>
      </div>
    </div>

  </div>
</template>

<style>
.app-container {
  display: flex;
  min-height: 100vh;
  width: 100vw;
  max-width: 100%;
  position: relative;
  overflow-x: hidden;
  overflow-y: auto;
  background: linear-gradient(180deg, #1a1f35 0%, #0f1419 100%);
}

.content-area {
  flex: 1;
  margin-left: 260px;
  width: calc(100vw - 260px);
  min-height: auto;
  display: flex;
  flex-direction: column;
  padding: 0 24px;
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1800px;
  margin: 0 auto;
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 24px 0;
  height: auto;
}

body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(180deg, #1a1f35 0%, #0f1419 100%);
  width: 100%;
  height: auto;
  overflow-y: auto;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #ffffff;
}

html {
  width: 100%;
  height: auto;
  background: linear-gradient(180deg, #1a1f35 0%, #0f1419 100%);
  overflow-y: auto;
  overflow-x: hidden;
}

#app {
  width: 100vw;
  min-height: auto;
  position: relative;
  background: linear-gradient(180deg, #1a1f35 0%, #0f1419 100%);
  margin: 0;
  padding: 0;
  max-width: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 媒体查询 */
@media screen and (max-width: 768px) {
  .content-area {
    margin-left: 60px;
    width: calc(100vw - 60px);
    padding: 0 5px;
    /* 减少水平内边距 */
    overflow-y: auto;
    /* 确保垂直滚动可用 */
  }

  .content-wrapper {
    padding: 10px 0;
    /* 减少垂直内边距 */
    overflow-y: visible;
    /* 确保内容可见 */
  }
}

/* 添加更小屏幕的优化 */
@media screen and (max-width: 480px) {
  .content-area {
    padding: 0 2px;
  }

  .content-wrapper {
    padding: 5px 0;
  }
}

/* 确保所有滚动容器都继承背景色 */
::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

/* 修改滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(15, 20, 25, 0.5);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 4px;
  transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
}

/* 联系作者按钮样式 */
.contact-author-container {
  position: fixed;
  top: 20px;
  right: 24px;
  z-index: 1000;
}

.contact-author-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: #ffffff;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transition: all 0.3s ease;
  user-select: none;
}

.contact-author-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
}

/* 二维码弹出层 */
.qr-code-popup {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  background: #ffffff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 1001;
  animation: slideDown 0.3s ease;
}

.qr-code-image {
  width: 200px;
  height: auto;
  display: block;
  border-radius: 8px;
}

/* 淡入动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .contact-author-container {
    top: 10px;
    right: 10px;
  }

  .qr-code-popup {
    right: -50px;
  }

  .qr-code-image {
    width: 160px;
  }
}
</style>
