<template>
  <div class="course-card" @click="$emit('click', course.id)">
    <div class="course-cover">
      <img :src="getImageUrl(course.img)" :alt="course.name" @error="handleImageError">
      <span class="course-tag" v-if="showTag && course.price === 0">免费</span>
      <span class="course-tag" v-if="showTag && course.score > 0">{{ course.score }}积分</span>
    </div>
    <div class="course-info">
      <h3 class="course-name">{{ course.name }}</h3>
      <p class="course-desc" v-if="showDesc">{{ course.description || '暂无描述' }}</p>
      <p class="course-price">
        <span class="price" v-if="course.price > 0">￥{{ course.price }}</span>
        <span class="free" v-else-if="course.price === 0">免费学习</span>
        <span class="free" v-else-if="course.score > 0">{{ course.score }} 积分</span>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CourseCard',
  props: {
    course: {
      type: Object,
      required: true
    },
    showTag: {
      type: Boolean,
      default: true
    },
    showDesc: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    // 处理图片URL，确保返回完整的URL路径
    getImageUrl(img) {
      if (!img) return require('@/assets/imgs/logo.png')
      return this.$getImageUrl(img)
    },
    // 图片加载失败时显示默认图
    handleImageError(e) {
      e.target.src = require('@/assets/imgs/logo.png')
    }
  }
}
</script>

<style scoped>
.course-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.2s;
}
.course-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.course-cover {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  overflow: hidden;
  background: #f1f5f9;
}
.course-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}
.course-card:hover .course-cover img {
  transform: scale(1.03);
}
.course-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #10b981;
  color: #fff;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 3px;
}
.course-info {
  padding: 14px;
}
.course-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin: 0 0 8px 0;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.course-desc {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.course-price {
  margin: 0;
}
.course-price .price {
  color: #ef4444;
  font-size: 16px;
  font-weight: 600;
}
.course-price .free {
  color: #10b981;
  font-size: 14px;
  font-weight: 500;
}
</style>
