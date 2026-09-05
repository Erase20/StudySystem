<template>
  <div class="main-content">
    <!-- Hero Banner 区域 -->
    <div class="hero-banner">
      <div class="hero-bg">
        <div class="hero-particles"></div>
        <div class="hero-content">
          <h1 class="hero-title">优质课程 <span class="highlight">免费学习</span></h1>
          <p class="hero-subtitle">海量精品课程，随时随地开启学习之旅</p>
          <div class="hero-search">
            <el-input
              placeholder="搜索你感兴趣的课程..."
              v-model="searchKeyword"
              prefix-icon="el-icon-search"
              class="hero-search-input"
              @keyup.enter.native="goSearch"
            >
              <el-button slot="append" @click="goSearch">搜索</el-button>
            </el-input>
          </div>
          <div class="hero-stats">
            <div class="stat-item">
              <span class="stat-num">{{ recommendCourses.length }}+</span>
              <span class="stat-label">精品课程</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num">免费</span>
              <span class="stat-label">开放学习</span>
            </div>
            <div class="stat-divider"></div>
            <div class="stat-item">
              <span class="stat-num">多</span>
              <span class="stat-label">课程分类</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- 课程分类快速入口 -->
      <div class="section-container">
        <div class="category-grid">
          <div class="category-item" v-for="cat in categories" :key="cat.key" @click="goCategory(cat.key)">
            <div class="category-icon" :style="{background: cat.bg}">
              <i :class="cat.icon"></i>
            </div>
            <span class="category-name">{{ cat.name }}</span>
          </div>
        </div>
      </div>

      <!-- 推荐课程区域 -->
      <div class="section-container">
        <div class="section-header">
          <div class="section-title">
            <h2>{{ directionTitle }}</h2>
          </div>
          <a href="/front/course" class="view-more">查看全部 →</a>
        </div>
        <!-- 骨架屏 -->
        <div class="skeleton-grid" v-if="loadingRecommend">
          <div class="skeleton-card" v-for="i in 8" :key="'sr'+i">
            <div class="skeleton skeleton-cover"></div>
            <div class="skeleton-body">
              <div class="skeleton skeleton-title"></div>
              <div class="skeleton skeleton-tag"></div>
            </div>
          </div>
        </div>
        <div class="course-grid" v-else>
          <div class="course-item" v-for="item in recommendCourses" :key="item.id" @click="navToCourse(item.id)">
            <div class="course-cover">
              <img :src="getImageUrl(item.img)" alt="" @error="handleImageError">
              <span class="cover-badge free" v-if="!item.price || item.price === 0">免费</span>
              <span class="cover-badge vip" v-else>VIP</span>
              <span class="cover-type">{{ item.category || '视频' }}</span>
            </div>
            <div class="course-info">
              <h3 class="course-name">{{ item.name }}</h3>
              <div class="course-meta">
                <span class="meta-tag free-tag" v-if="!item.price || item.price === 0">免费学习</span>
                <span class="meta-tag vip-tag" v-else>VIP课程</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 精选课程区域 -->
      <div class="section-container">
        <div class="section-header">
          <div class="section-title">
            <h2>精选课程</h2>
          </div>
           <div class="filter-tabs">
            <span :class="{active: !featuredCategory}" @click="setFeaturedCategory(null)">全部</span>
            <span :class="{active: featuredCategory === 'Python开发'}" @click="setFeaturedCategory('Python开发')">Python</span>
            <span :class="{active: featuredCategory === 'Java开发'}" @click="setFeaturedCategory('Java开发')">Java</span>
            <span :class="{active: featuredCategory === '人工智能'}" @click="setFeaturedCategory('人工智能')">人工智能</span>
            <span :class="{active: featuredCategory === '前端开发'}" @click="setFeaturedCategory('前端开发')">前端</span>
          </div>
          <el-button class="signin-btn" @click="signin" v-if="user.username">
            <i class="el-icon-check"></i> 每日签到
          </el-button>
        </div>
        <!-- 骨架屏 -->
        <div class="skeleton-grid" v-if="loadingFeatured">
          <div class="skeleton-card" v-for="i in 4" :key="'sf'+i">
            <div class="skeleton skeleton-cover"></div>
            <div class="skeleton-body">
              <div class="skeleton skeleton-title"></div>
            </div>
          </div>
        </div>
        <div class="course-grid featured-grid" v-else>
          <div class="course-item featured" @click="navTo(recommend.id)" v-if="recommend && recommend.id">
            <div class="course-cover">
              <img :src="getImageUrl(recommend.img)" alt="" @error="handleImageError">
              <span class="cover-badge free" v-if="!recommend.price || recommend.price === 0">免费</span>
              <span class="cover-badge vip" v-else>VIP</span>
            </div>
            <div class="course-info">
              <h3 class="course-name">{{ recommend.name }}</h3>
              <p class="course-desc">高质量视频课程，助你快速掌握</p>
              <span class="meta-tag free-tag" v-if="!recommend.price || recommend.price === 0">免费学习</span>
              <span class="meta-tag vip-tag" v-else>VIP课程</span>
            </div>
          </div>
          <div class="course-item" v-for="item in rightData" :key="item.id" @click="navTo(item.id)">
            <div class="course-cover">
              <img :src="getImageUrl(item.img)" alt="" @error="handleImageError">
              <span class="cover-badge free" v-if="!item.price || item.price === 0">免费</span>
              <span class="cover-badge vip" v-else>VIP</span>
            </div>
            <div class="course-info">
              <h3 class="course-name">{{ item.name }}</h3>
            </div>
          </div>
        </div>
      </div>

      <!-- 学习资料区域 -->
      <div class="section-container">
        <div class="section-header">
          <div class="section-title">
            <h2>学习资料</h2>
          </div>
          <a href="/front/information" class="view-more">查看更多 →</a>
        </div>
        <!-- 骨架屏 -->
        <div class="skeleton-grid" v-if="loadingInfo">
          <div class="skeleton-card" v-for="i in 4" :key="'si'+i">
            <div class="skeleton skeleton-cover"></div>
            <div class="skeleton-body">
              <div class="skeleton skeleton-title"></div>
              <div class="skeleton skeleton-tag"></div>
            </div>
          </div>
        </div>
        <div class="course-grid" v-else>
          <div class="course-item" v-for="item in leftData" :key="item.id" @click="NavToInformation(item.id)">
            <div class="course-cover">
              <img :src="getImageUrl(item.img)" alt="" @error="handleImageError">
              <span class="cover-badge free">资料</span>
            </div>
            <div class="course-info">
              <h3 class="course-name">{{ item.name }}</h3>
              <div class="course-meta">
                <span class="meta-tag free-tag">免费下载</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 首页组件
 * 展示推荐课程、精选课程、学习资料
 */
export default {
  data() {
    return {
      user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
      searchKeyword: '',
      categories: [
        { key: 'Python开发', name: 'Python', icon: 'el-icon-data-line', bg: 'linear-gradient(135deg, #10b981, #059669)' },
        { key: 'Java开发', name: 'Java', icon: 'el-icon-coffee-cup', bg: 'linear-gradient(135deg, #f97316, #ea580c)' },
        { key: '人工智能', name: 'AI', icon: 'el-icon-cpu', bg: 'linear-gradient(135deg, #6366f1, #4f46e5)' },
        { key: '前端开发', name: '前端', icon: 'el-icon-monitor', bg: 'linear-gradient(135deg, #3b82f6, #2563eb)' },
        { key: '爬虫与自动化', name: '爬虫', icon: 'el-icon-connection', bg: 'linear-gradient(135deg, #ec4899, #db2777)' },
        { key: '软件测试', name: '测试', icon: 'el-icon-finished', bg: 'linear-gradient(135deg, #14b8a6, #0d9488)' },
        { key: '数据库', name: '数据库', icon: 'el-icon-coin', bg: 'linear-gradient(135deg, #8b5cf6, #7c3aed)' },
        { key: 'Linux运维', name: 'Linux', icon: 'el-icon-office-building', bg: 'linear-gradient(135deg, #f59e0b, #d97706)' },
      ],
      carouselData: [],
      type: 'VIDEO',
      featuredCategory: null,
      recommend: {},
      rightData: [],
      fileRecommend: {},
      leftData: [],
      signInData: {},
      recommendCourses: [],
      loadingRecommend: true,
      loadingFeatured: true,
      loadingInfo: true,
    }
  },
  
  mounted() {
    this.getData()
    this.getInformation()
    this.getRecommendCourses()
    this.getCarouselCourses()
    if (this.user.id) {
      this.getSign()
    }
  },

  computed: {
    directionTitle() {
      const direction = this.user.direction
      if (direction) {
        const dirs = direction.split(',').slice(0, 3).join(' / ')
        return '为你推荐 · ' + dirs
      }
      return this.user.username ? '为你推荐' : '热门课程'
    }
  },
  
  methods: {
    getCarouselCourses() {
      this.$request.get('/course/selectTop8?type=VIDEO').then(res => {
        if (res.code === '200') {
          this.carouselData = res.data || []
        }
      }).catch(() => {
        this.carouselData = []
      })
    },
    
    navToCarousel(item) {
      if (item.type === 'SCORE') {
        this.$router.push({ path: '/front/scoreDetail', query: { id: item.id } })
      } else {
        this.$router.push({ path: '/front/courseDetail', query: { id: item.id } })
      }
    },
    
    handleCarouselImageError(e, item) {
      e.target.src = require('@/assets/imgs/lun-1.jpg')
    },
    
    getSign() {
      this.$request.get('/signin/selectByUserId?id=' + this.user.id).then(res => {
        if (res.code === '200') {
          this.signInData = res.data
        }
      }).catch(() => {})
    },
    
    signin() {
      let data = { userId: this.user.id }
      this.$request.post('/signin/add', data).then(res => {
        if (res.code === '200') {
          this.$message.success('签到成功，获得10积分')
          this.getSign()
        } else {
          this.$message.error(res.msg)
        }
      }).catch(() => {})
    },
    
    NavToInformation(id) {
      this.$router.push({ path: '/front/informationDetail', query: { id } })
    },
    
    navTo(id) {
      if (this.type === 'SCORE') {
        this.$router.push({ path: '/front/scoreDetail', query: { id } })
      } else {
        this.$router.push({ path: '/front/courseDetail', query: { id } })
      }
    },
    
    navToCourse(id) {
      this.$router.push({ path: '/front/courseDetail', query: { id } })
    },
    
    /**
     * 获取推荐课程 - 智能推荐算法（优先按学习方向推荐）
     */
    getRecommendCourses() {
      this.loadingRecommend = true
      // 获取用户学习方向
      const user = JSON.parse(localStorage.getItem('xm-user') || '{}')
      const direction = user.direction || ''
      
      this.$request.get('/analysis/smart-recommend?limit=8').then(res => {
        if (res.code === '200') {
          let courses = res.data && res.data.courses ? res.data.courses : (res.data || [])
          // 按学习方向优先排序
          if (direction && courses.length > 0) {
            const dirs = direction.split(',')
            courses = this.sortByDirection(courses, dirs)
          }
          this.recommendCourses = courses
        }
      }).catch(() => {
        this.$request.get('/course/recommend?limit=8').then(res => {
          if (res.code === '200') {
            let courses = res.data || []
            if (direction && courses.length > 0) {
              const dirs = direction.split(',')
              courses = this.sortByDirection(courses, dirs)
            }
            this.recommendCourses = courses
          }
        }).catch(() => {
          this.recommendCourses = []
        })
      }).finally(() => {
        this.loadingRecommend = false
      })
    },
    
    /**
     * 按学习方向优先排序课程
     * 匹配方向的课程排前面，其余保持原序
     */
    sortByDirection(courses, directions) {
      const matched = []
      const unmatched = []
      courses.forEach(course => {
        const name = (course.name || '').toLowerCase()
        const isMatch = directions.some(dir => name.includes(dir.toLowerCase()))
        if (isMatch) {
          matched.push(course)
        } else {
          unmatched.push(course)
        }
      })
      return [...matched, ...unmatched]
    },
    
    setFeaturedCategory(category) {
      this.featuredCategory = category
      this.getData()
    },
    
    initValue(type) {
      this.type = type
      this.getData()
    },
    
    getData() {
      this.loadingFeatured = true
      let params = []
      if (this.type) params.push('type=' + this.type)
      if (this.featuredCategory) params.push('category=' + encodeURIComponent(this.featuredCategory))
      let query = params.length ? '?' + params.join('&') : ''
      this.getRecommend('/course/getRecommend' + query)
      this.getRightData('/course/selectTop8' + query)
    },
    
    getInformation() {
      this.loadingInfo = true
      this.$request.get('/information/getRecommend').then(res => {
        if (res.code === '200') {
          this.fileRecommend = res.data
        }
      }).catch(() => {})
      this.$request.get('/information/selectTop8').then(res => {
        if (res.code === '200') {
          this.leftData = res.data
        }
      }).catch(() => {}).finally(() => {
        this.loadingInfo = false
      })
    },
    
    getRecommend(url) {
      this.$request.get(url).then(res => {
        if (res.code === '200') {
          this.recommend = res.data
        }
      }).catch(() => {})
    },
    
    getRightData(url) {
      this.$request.get(url).then(res => {
        if (res.code === '200') {
          this.rightData = res.data
        }
      }).catch(() => {}).finally(() => {
        this.loadingFeatured = false
      })
    },
    
    getImageUrl(img) {
      if (!img) return require('@/assets/imgs/logo.png')
      return this.$getImageUrl(img)
    },
    
    handleImageError(e) {
      e.target.src = require('@/assets/imgs/logo.png')
    },
    
    goSearch() {
      if (this.searchKeyword.trim()) {
        this.$router.push({ path: '/front/course', query: { name: this.searchKeyword.trim() } })
      }
    },
    
    goCategory(key) {
      if (key) {
        this.$router.push({ path: '/front/course', query: { category: key } })
      } else {
        this.$router.push('/front/course')
      }
    }
  }
}
</script>

<style scoped>
/* ========== Hero Banner ========== */
.hero-banner {
  position: relative;
  overflow: hidden;
}

.hero-bg {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #334155 100%);
  padding: 64px 24px 56px;
  position: relative;
}

.hero-particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.12) 0%, transparent 50%),
    radial-gradient(circle at 60% 80%, rgba(16, 185, 129, 0.1) 0%, transparent 50%);
}

.hero-content {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 42px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 16px 0;
  letter-spacing: -0.5px;
}

.hero-title .highlight {
  background: linear-gradient(135deg, #34d399, #10b981);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 18px;
  color: rgba(255,255,255,0.7);
  margin: 0 0 32px 0;
}

.hero-search {
  max-width: 520px;
  margin: 0 auto 32px;
}

.hero-search-input :deep(.el-input__inner) {
  height: 48px;
  border-radius: 24px 0 0 24px !important;
  border: none;
  font-size: 15px;
  padding-left: 44px;
}

.hero-search-input :deep(.el-input-group__append) {
  background: #10b981;
  border: none;
  color: #fff;
  font-size: 15px;
  font-weight: 500;
  border-radius: 0 24px 24px 0 !important;
  padding: 0 28px;
  cursor: pointer;
}

.hero-search-input :deep(.el-input-group__append:hover) {
  background: #059669;
}

.hero-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 32px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  font-size: 13px;
  color: rgba(255,255,255,0.6);
  margin-top: 4px;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: rgba(255,255,255,0.2);
}

/* ========== 课程分类入口 ========== */
.category-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 16px;
  margin-top: -36px;
  position: relative;
  z-index: 10;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 8px;
  background: #fff;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.category-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.category-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.category-icon i {
  font-size: 22px;
  color: #fff;
}

.category-name {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
}

/* ========== 内容区域 ========== */
.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 24px 48px;
  background: #fff;
}

.section-container {
  margin-bottom: 48px;
}

/* 区块标题 */
.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.section-title h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.view-more {
  margin-left: auto;
  color: #64748b;
  font-size: 14px;
  text-decoration: none;
  transition: color 0.3s;
}

.view-more:hover {
  color: #10b981;
}

/* 标签切换 */
.filter-tabs {
  margin-left: 32px;
  display: flex;
  gap: 0;
  border-bottom: 1px solid #e2e8f0;
}

.filter-tabs span {
  cursor: pointer;
  color: #94a3b8;
  font-size: 14px;
  padding: 8px 16px;
  position: relative;
  transition: color 0.3s;
}

.filter-tabs span:hover {
  color: #64748b;
}

.filter-tabs span.active {
  color: #1e293b;
  font-weight: 500;
}

.filter-tabs span.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #1e293b;
}

/* 签到按钮 */
.signin-btn {
  margin-left: auto;
  background: linear-gradient(135deg, #10b981, #059669) !important;
  border: none !important;
  color: #fff !important;
  padding: 8px 16px !important;
  border-radius: 20px !important;
  font-size: 13px !important;
}

.signin-btn:hover {
  background: linear-gradient(135deg, #059669, #047857) !important;
}

/* ========== 课程网格 ========== */
.course-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

/* 课程卡片 */
.course-item {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.course-item:hover {
  border-color: #10b981;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.12);
  transform: translateY(-4px);
}

.course-item.featured {
  grid-column: span 2;
  grid-row: span 2;
}

/* 课程封面 */
.course-cover {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  overflow: hidden;
  background: #f1f5f9;
}

.course-item.featured .course-cover {
  padding-top: 65%;
}

.course-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.course-item:hover .course-cover img {
  transform: scale(1.05);
}

/* 封面角标 */
.cover-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 4px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.cover-badge.free {
  background: rgba(16, 185, 129, 0.9);
  color: #fff;
}

.cover-badge.vip {
  background: rgba(245, 158, 11, 0.9);
  color: #fff;
}

.cover-type {
  position: absolute;
  bottom: 10px;
  right: 10px;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  background: rgba(0,0,0,0.5);
  color: #fff;
}

/* 课程信息 */
.course-info {
  padding: 14px 16px;
}

.course-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin: 0 0 8px 0;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-item.featured .course-name {
  font-size: 16px;
  white-space: normal;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.course-desc {
  font-size: 13px;
  color: #64748b;
  margin: 8px 0 0 0;
  line-height: 1.6;
}

/* 课程元信息标签 */
.course-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-tag {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 4px;
  font-weight: 500;
}

.meta-tag.free-tag {
  background: #ecfdf5;
  color: #059669;
}

.meta-tag.vip-tag {
  background: #fffbeb;
  color: #d97706;
}

/* ========== 骨架屏 ========== */
.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.skeleton-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.skeleton-cover {
  width: 100%;
  height: 0;
  padding-top: 56.25%;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-body {
  padding: 16px;
}

.skeleton-title {
  height: 16px;
  width: 80%;
  margin-bottom: 12px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

.skeleton-tag {
  height: 14px;
  width: 50%;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ========== 响应式 ========== */
@media (max-width: 1200px) {
  .course-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .category-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 900px) {
  .course-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  .course-item.featured {
    grid-column: span 2;
    grid-row: span 1;
  }
  .filter-tabs {
    margin-left: 0;
    margin-top: 16px;
  }
  .section-header {
    flex-wrap: wrap;
  }
  .category-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 600px) {
  .hero-bg {
    padding: 40px 16px 48px;
  }
  .hero-title {
    font-size: 28px;
  }
  .hero-subtitle {
    font-size: 15px;
  }
  .content-wrapper {
    padding: 32px 16px;
  }
  .course-grid {
    grid-template-columns: 1fr;
  }
  .course-item.featured {
    grid-column: span 1;
  }
  .category-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
  }
  .category-item {
    padding: 14px 4px;
  }
  .category-icon {
    width: 36px;
    height: 36px;
  }
  .category-icon i {
    font-size: 18px;
  }
  .category-name {
    font-size: 12px;
  }
  .hero-stats {
    gap: 20px;
  }
  .stat-num {
    font-size: 20px;
  }
}
</style>
