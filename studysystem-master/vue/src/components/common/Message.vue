<template>
  <div v-if="message.show" class="message-container" :class="`message-${message.type}`">
    <div class="message-content">
      <i :class="getIconClass" class="message-icon"></i>
      <span class="message-text">{{ message.content }}</span>
      <i class="el-icon-close message-close" @click="closeMessage"></i>
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    message() {
      return this.$store.getters['common/message']
    },
    getIconClass() {
      const iconMap = {
        success: 'el-icon-check-circle',
        warning: 'el-icon-warning',
        error: 'el-icon-error',
        info: 'el-icon-info'
      }
      return iconMap[this.message.type] || 'el-icon-info'
    }
  },
  methods: {
    closeMessage() {
      this.$store.commit('common/HIDE_MESSAGE')
    }
  }
}
</script>

<style scoped>
.message-container {
  position: fixed;
  top: 80px;
  right: 24px;
  z-index: 2000;
  min-width: 300px;
  max-width: 500px;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  animation: slideIn 0.3s ease;
}

.message-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.message-icon {
  font-size: 18px;
}

.message-text {
  flex: 1;
  font-size: 14px;
  line-height: 1.5;
}

.message-close {
  font-size: 16px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s;
}

.message-close:hover {
  opacity: 1;
}

/* 不同类型的消息样式 */
.message-success {
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
  color: #67c23a;
}

.message-warning {
  background: #fdf6ec;
  border: 1px solid #faecd8;
  color: #e6a23c;
}

.message-error {
  background: #fef0f0;
  border: 1px solid #fde2e2;
  color: #f56c6c;
}

.message-info {
  background: #f4f4f5;
  border: 1px solid #ebeef5;
  color: #909399;
}

/* 动画 */
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 响应式 */
@media (max-width: 600px) {
  .message-container {
    right: 16px;
    left: 16px;
    min-width: auto;
  }
}
</style>