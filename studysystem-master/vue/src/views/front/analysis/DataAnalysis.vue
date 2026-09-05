<template>
  <div class="analysis-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>智能学习分析</h2>
      <p>基于AI算法的个性化学习推荐与数据分析</p>
    </div>

    <!-- 用户画像卡片 -->
    <div class="profile-section">
      <div class="section-title">
        <span class="title-icon">◆</span>
        <span>我的学习画像</span>
      </div>
      <div class="profile-card" v-if="profile.name">
        <div class="profile-avatar">
          <img :src="getImageUrl(profile.avatar)" alt="">
        </div>
        <div class="profile-info">
          <h3>{{ profile.name }}</h3>
          <div class="profile-tags">
            <span class="tag" v-for="tag in profile.tags" :key="tag">{{ tag }}</span>
          </div>
          <div class="profile-stats">
            <div class="stat-item">
              <span class="stat-value">{{ profile.orderCount || 0 }}</span>
              <span class="stat-label">已购课程</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ profile.activityScore || 0 }}</span>
              <span class="stat-label">活跃度</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">¥{{ (profile.totalSpent || 0).toFixed(0) }}</span>
              <span class="stat-label">累计消费</span>
            </div>
          </div>
        </div>
        <div class="activity-bar">
          <div class="activity-label">活跃度评分</div>
          <el-progress 
            :percentage="profile.activityScore || 0" 
            :stroke-width="8"
          ></el-progress>
        </div>
      </div>
    </div>

    <!-- 学习进度分析 -->
    <div class="progress-section">
      <div class="section-title">
        <span class="title-icon">◆</span>
        <span>学习进度分析</span>
      </div>
      <div class="progress-card">
        <div class="progress-stats">
          <div class="progress-item">
            <el-progress 
              type="circle" 
              :percentage="parseFloat(learningProgress.predictedCompletionRate) || 0"
              :width="80"
              :stroke-width="8"
            ></el-progress>
            <div class="progress-label">预测完成率</div>
          </div>
          <div class="progress-item">
            <div class="stat-number">{{ learningProgress.totalCourses || 0 }}</div>
            <div class="stat-label">已购课程</div>
          </div>
          <div class="progress-item">
            <div class="stat-number">{{ learningProgress.completedCourses || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="progress-item">
            <div class="stat-number">{{ learningProgress.learningStreak || 0 }}</div>
            <div class="stat-label">连续学习(天)</div>
          </div>
        </div>
        <div class="suggestions" v-if="learningProgress.suggestions">
          <div class="suggestion-title">学习建议</div>
          <ul>
            <li v-for="(suggestion, index) in learningProgress.suggestions" :key="index">
              {{ suggestion }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 学习路径推荐 -->
    <div class="path-section">
      <div class="section-title">
        <span class="title-icon">◆</span>
        <span>学习路径规划</span>
      </div>
      <div class="path-timeline">
        <div 
          class="path-stage" 
          v-for="(stage, index) in learningPath.learningPath" 
          :key="index"
          :class="{'completed': stage.status === '已完成', 'current': stage.status === '进行中'}"
        >
          <div class="stage-header">
            <div class="stage-level">{{ stage.name }}</div>
            <span class="stage-status" :class="stage.status">{{ stage.status }}</span>
          </div>
          <div class="stage-courses" v-if="stage.courses && stage.courses.length > 0">
            <div 
              class="stage-course" 
              v-for="course in stage.courses" 
              :key="course.id"
              @click="goToCourse(course.id)"
            >
              <img :src="getImageUrl(course.img)" alt="">
              <span>{{ course.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 智能推荐课程 -->
    <div class="recommend-section">
      <div class="section-title">
        <span class="title-icon">◆</span>
        <span>{{ smartRecommend.reason || '智能推荐' }}</span>
      </div>
      <div class="recommend-grid">
        <div 
          class="recommend-item" 
          v-for="course in smartRecommend.courses" 
          :key="course.id"
          @click="goToCourse(course.id)"
        >
          <div class="recommend-cover">
            <img :src="getImageUrl(course.img)" alt="">
          </div>
          <div class="recommend-info">
            <h4>{{ course.name }}</h4>
            <div class="recommend-meta">
              <span class="recommend-type">{{ course.category || '视频' }}</span>
              <span class="recommend-price" v-if="course.price > 0">¥{{ course.price }}</span>
              <span class="recommend-free" v-else>免费</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 智能学习分析页面
 * 功能：用户画像、学习进度分析、学习路径规划、智能推荐
 */
export default {
  name: 'DataAnalysis',
  
  data() {
    return {
      profile: {},
      learningProgress: {},
      learningPath: {},
      smartRecommend: { courses: [], reason: '', strategy: '' },
      user: JSON.parse(localStorage.getItem('xm-user') || '{}')
    }
  },
  
  created() {
    this.loadAllData()
  },
  
  methods: {
    loadAllData() {
      this.getUserProfile()
      this.getLearningProgress()
      this.getLearningPath()
      this.getSmartRecommend()
    },
    
    getUserProfile() {
      this.$request.get('/analysis/profile').then(res => {
        console.log('用户画像:', res)
        if (res.code === '200') {
          this.profile = res.data || {}
        }
      }).catch(err => {
        console.error('用户画像错误:', err)
      })
    },
    
    getLearningProgress() {
      this.$request.get('/analysis/learning-progress').then(res => {
        console.log('学习进度:', res)
        if (res.code === '200') {
          this.learningProgress = res.data || {}
        }
      }).catch(err => {
        console.error('学习进度错误:', err)
      })
    },
    
    getLearningPath() {
      this.$request.get('/analysis/learning-path').then(res => {
        console.log('学习路径:', res)
        if (res.code === '200') {
          this.learningPath = res.data || {}
        }
      }).catch(err => {
        console.error('学习路径错误:', err)
      })
    },
    
    getSmartRecommend() {
      this.$request.get('/analysis/smart-recommend?limit=8').then(res => {
        console.log('智能推荐:', res)
        if (res.code === '200') {
          this.smartRecommend = res.data || { courses: [], reason: '', strategy: '' }
        }
      }).catch(err => {
        console.error('智能推荐错误:', err)
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
/* 页面容器 */
.analysis-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

/* 页面标题 */
.page-header {
  margin-bottom: 32px;
}

.page-header h2 {
  font-size: 24px;
  color: #1e293b;
  margin-bottom: 8px;
}

.page-header p {
  color: #64748b;
  font-size: 14px;
}

/* 区块标题 */
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
}

.title-icon {
  color: #1e293b;
  font-size: 12px;
}

/* 用户画像卡片 */
.profile-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.profile-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-info {
  flex: 1;
}

.profile-info h3 {
  font-size: 20px;
  color: #1e293b;
  margin-bottom: 12px;
}

.profile-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.tag {
  font-size: 12px;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 10px;
  border-radius: 4px;
}

.profile-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
}

.stat-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 4px;
}

.activity-bar {
  width: 180px;
  padding-top: 8px;
}

.activity-label {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
}

/* 学习进度卡片 */
.progress-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
}

.progress-stats {
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-bottom: 24px;
}

.progress-item {
  text-align: center;
}

.progress-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
}

.suggestions {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
}

.suggestion-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.suggestions li {
  color: #64748b;
  line-height: 1.8;
}

/* 学习路径时间线 */
.path-timeline {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.path-stage {
  min-width: 200px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
}

.path-stage.completed {
  border-left: 3px solid #1e293b;
}

.path-stage.current {
  border-left: 3px solid #1e293b;
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stage-level {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.stage-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f1f5f9;
  color: #64748b;
}

.stage-status.已完成 {
  background: #1e293b;
  color: #fff;
}

.stage-status.进行中 {
  background: #1e293b;
  color: #fff;
}

.stage-courses {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stage-course {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8fafc;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.stage-course:hover {
  background: #f1f5f9;
}

.stage-course img {
  width: 36px;
  height: 24px;
  border-radius: 4px;
  object-fit: cover;
}

.stage-course span {
  font-size: 12px;
  color: #475569;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 推荐课程网格 */
.recommend-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.recommend-item {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.recommend-item:hover {
  border-color: #1e293b;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.recommend-cover {
  position: relative;
  padding-top: 56.25%;
  overflow: hidden;
}

.recommend-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recommend-info {
  padding: 12px;
}

.recommend-info h4 {
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommend-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recommend-type {
  font-size: 12px;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}

.recommend-price {
  font-size: 14px;
  font-weight: 600;
  color: #dc2626;
}

.recommend-free {
  font-size: 12px;
  color: #1e293b;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 1024px) {
  .recommend-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .profile-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .profile-stats {
    justify-content: center;
  }
  .activity-bar {
    width: 100%;
  }
  .recommend-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .recommend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
