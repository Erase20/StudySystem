<template>
  <div class="empty-state">
    <i :class="icon"></i>
    <p class="empty-text">{{ text }}</p>
    <el-button v-if="showButton" type="primary" @click="$emit('action')">
      {{ buttonText }}
    </el-button>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    icon: {
      type: String,
      default: 'el-icon-box'
    },
    text: {
      type: String,
      default: '暂无数据'
    },
    showButton: {
      type: Boolean,
      default: false
    },
    buttonText: {
      type: String,
      default: '去逛逛'
    }
  }
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #94a3b8;
}
.empty-state i {
  font-size: 64px;
  margin-bottom: 16px;
}
.empty-text {
  font-size: 14px;
  margin: 0 0 20px 0;
}
</style>
