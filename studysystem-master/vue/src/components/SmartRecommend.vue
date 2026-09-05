<template>
  <div class="smart-recommend">
    <!-- 推荐标题 -->
    <div class="recommend-header">
      <div class="recommend-title">
        <span class="title-icon">◆</span>
        <span>{{ title || '智能推荐' }}</span>
      </div>
    </div>
    
    <!-- 推荐课程列表 -->
    <div class="recommend-list" v-loading="loading">
      <div 
        class="recommend-card" 
        v-for="course in courses" 
        :key="course.id"
        @click="goToCourse(course.id)"
      >
        <div class="card-cover">
          <img :src="getImageUrl(course.img)" alt="">
        </div>
        <div class="card-content">
          <h4 class="card-title">{{ course.name }}</h4>
          <div class="card-meta">
            <span class="card-type">{{ course.category || '视频' }}</span>
            <span class="card-price" v-if="course.price > 0">¥{{ course.price }}</span>
            <span class="card-free" v-else>免费</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div class="recommend-empty" v-if="!loading && courses.length === 0">
      <p>暂无推荐课程</p>
    </div>
  </div>
</template>

<script>
/**
 * 智能推荐组件
 */
export default {
  name: 'SmartRecommend',
  
  props: {
    title: {
      type: String,
      default: '智能推荐'
    },
    limit: {
      type: Number,
      default: 8
    },
    type: {
      type: String,
      default: 'smart'
    }
  },
  
  data() {
    return {
      courses: [],
      strategy: '',
      loading: false
    }
  },
  
  created() {
    this.loadRecommendations()
  },
  
  methods: {
    loadRecommendations() {
      this.loading = true
      
      let apiUrl = '/analysis/smart-recommend'
      if (this.type === 'cold') {
        apiUrl = '/analysis/cold-start'
      } else if (this.type === 'hot') {
        apiUrl = '/analysis/time-decay-hot'
      }
      
      this.$request.get(`${apiUrl}?limit=${this.limit}`).then(res => {
        if (res.code === '200') {
          if (res.data.courses) {
            this.courses = res.data.courses || []
            this.strategy = res.data.strategy || ''
          } else {
            this.courses = res.data || []
          }
        }
      }).catch(() => {
        this.courses = []
      }).finally(() => {
        this.loading = false
      })
    },
    
    getImageUrl(img) {
      if (!img) return require('@/assets/imgs/logo.png')
      return this.$getImageUrl(img)
    },
    
    goToCourse(courseId) {
      this.$router.push('/front/courseDetail?id=' + courseId)
    }
  }
}
</script>

<style scoped>
.smart-recommend {
  margin: 20px 0;
}

.recommend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.recommend-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.title-icon {
  color: #1e293b;
  font-size: 12px;
}

.recommend-list {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.recommend-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.recommend-card:hover {
  border-color: #1e293b;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.card-cover {
  position: relative;
  padding-top: 56.25%;
  overflow: hidden;
}

.card-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  padding: 12px;
}

.card-title {
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-type {
  font-size: 12px;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}

.card-price {
  font-size: 14px;
  font-weight: 600;
  color: #dc2626;
}

.card-free {
  font-size: 12px;
  color: #1e293b;
  font-weight: 500;
}

.recommend-empty {
  text-align: center;
  padding: 40px 0;
  color: #94a3b8;
}

@media (max-width: 1200px) {
  .recommend-list {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .recommend-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .recommend-list {
    grid-template-columns: 1fr;
  }
}
</style>
