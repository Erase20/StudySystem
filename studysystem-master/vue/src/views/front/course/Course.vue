<template>
  <div class="course-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>全部课程</h2>
      <p>探索丰富的学习资源，开启知识之旅</p>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <!-- 分类筛选 -->
        <div class="filter-group">
          <span class="filter-label">分类</span>
          <div class="filter-tags">
            <span :class="['filter-tag', { active: !category }]" @click="setCategory(null)">全部</span>
            <span :class="['filter-tag', { active: category === 'Python开发' }]" @click="setCategory('Python开发')">Python开发</span>
            <span :class="['filter-tag', { active: category === 'Java开发' }]" @click="setCategory('Java开发')">Java开发</span>
            <span :class="['filter-tag', { active: category === '人工智能' }]" @click="setCategory('人工智能')">人工智能</span>
            <span :class="['filter-tag', { active: category === '爬虫与自动化' }]" @click="setCategory('爬虫与自动化')">爬虫与自动化</span>
            <span :class="['filter-tag', { active: category === '前端开发' }]" @click="setCategory('前端开发')">前端开发</span>
            <span :class="['filter-tag', { active: category === '软件测试' }]" @click="setCategory('软件测试')">软件测试</span>
            <span :class="['filter-tag', { active: category === '数据库' }]" @click="setCategory('数据库')">数据库</span>
            <span :class="['filter-tag', { active: category === 'Linux运维' }]" @click="setCategory('Linux运维')">Linux运维</span>
            <span :class="['filter-tag', { active: category === '数据结构' }]" @click="setCategory('数据结构')">数据结构</span>
          </div>
        </div>
        <!-- 排序 -->
        <div class="filter-group">
          <span class="filter-label">排序</span>
          <div class="filter-tags">
            <span :class="['filter-tag', { active: sort === 'latest' }]" @click="setSort('latest')">最新</span>
            <span :class="['filter-tag', { active: sort === 'free' }]" @click="setSort('free')">免费优先</span>
          </div>
        </div>
      </div>
      <!-- 搜索 -->
      <div class="filter-search">
        <el-input 
          placeholder="搜索课程名称" 
          v-model="name"
          prefix-icon="el-icon-search"
          clearable
          @keyup.enter.native="load(1)"
          @clear="load(1)"
        ></el-input>
      </div>
    </div>

    <!-- 课程卡片网格 -->
    <div class="course-grid" v-if="tableData.length">
      <div class="course-card" v-for="item in tableData" :key="item.id" @click="goDetail(item)">
        <div class="card-cover">
          <img :src="getImageUrl(item.img)" alt="" @error="handleImgError">
          <span class="card-badge free-badge" v-if="!item.price || item.price === 0">免费</span>
          <span class="card-badge vip-badge" v-else>VIP</span>
          <span class="card-type-tag">{{ item.category || '视频' }}</span>
        </div>
        <div class="card-body">
          <h3 class="card-name">{{ item.name }}</h3>
          <div class="card-meta">
            <span class="card-time">{{ item.time }}</span>
          </div>
          <div class="card-tag-row">
            <span class="card-free-tag" v-if="!item.price || item.price === 0">免费学习</span>
            <span class="card-vip-tag" v-else>VIP课程</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-if="!loading && !tableData.length">
      <i class="el-icon-search"></i>
      <p>暂无课程数据</p>
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="total > 0">
      <el-pagination
        background
        @current-change="handleCurrentChange"
        :current-page="pageNum"
        :page-size="pageSize"
        layout="total, prev, pager, next"
        :total="total"
      ></el-pagination>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tableData: [],
      pageNum: 1,
      pageSize: 12,
      total: 0,
      name: null,
      category: null,
      sort: 'latest',
      loading: false,
      user: JSON.parse(localStorage.getItem('xm-user') || '{}')
    }
  },
  
  mounted() {
    // 支持从首页搜索跳转带参数
    if (this.$route.query.name) {
      this.name = this.$route.query.name
    }
    // 支持从首页分类跳转
    if (this.$route.query.category) {
      this.category = this.$route.query.category
    }
    this.load(1)
  },
  
  methods: {
    setCategory(category) {
      this.category = category
      this.load(1)
    },
    
    setSort(sort) {
      this.sort = sort
      this.load(1)
    },
    
    load(pageNum) {
      if (pageNum) this.pageNum = pageNum
      this.loading = true
      this.$request.get('/course/selectPage', {
        params: {
          pageNum: this.pageNum,
          pageSize: this.pageSize,
          name: this.name,
          category: this.category
        }
      }).then(res => {
        let list = res.data?.list || []
        // 前端排序
      if (this.sort === 'free') {
          list.sort((a, b) => (a.price || 0) - (b.price || 0))
        }
        this.tableData = list
        this.total = res.data?.total || 0
      }).catch(() => {}).finally(() => {
        this.loading = false
      })
    },
    
    goDetail(item) {
      this.$router.push({ path: '/front/courseDetail', query: { id: item.id } })
    },
    
    handleCurrentChange(pageNum) {
      this.load(pageNum)
    },
    
    handleImgError(e) {
      e.target.src = require('@/assets/imgs/logo.png')
    },
    
    getImageUrl(img) {
      if (!img) return require('@/assets/imgs/logo.png')
      return this.$getImageUrl(img)
    }
  }
}
</script>

<style scoped>
.course-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  background: #fff;
}

.page-header {
  margin-bottom: 28px;
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

/* 筛选栏 */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
  gap: 24px;
  flex-wrap: wrap;
}

.filter-left {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  color: #64748b;
  white-space: nowrap;
  min-width: 32px;
}

.filter-tags {
  display: flex;
  gap: 0;
  border-bottom: 1px solid #e2e8f0;
}

.filter-tag {
  cursor: pointer;
  color: #94a3b8;
  font-size: 14px;
  padding: 6px 16px;
  position: relative;
  transition: color 0.3s;
  white-space: nowrap;
}

.filter-tag:hover {
  color: #64748b;
}

.filter-tag.active {
  color: #1e293b;
  font-weight: 500;
}

.filter-tag.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: #10b981;
}

.filter-search {
  min-width: 240px;
}

.filter-search .el-input__inner {
  border-radius: 20px !important;
}

/* 课程网格 - 3列MOOC风格 */
.course-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

/* 课程卡片 */
.course-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.course-card:hover {
  border-color: #10b981;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.12);
  transform: translateY(-4px);
}

.card-cover {
  position: relative;
  width: 100%;
  padding-top: 56.25%;
  overflow: hidden;
  background: #f1f5f9;
}

.card-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.course-card:hover .card-cover img {
  transform: scale(1.05);
}

/* 封面角标 */
.card-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 4px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.card-badge.free-badge {
  background: rgba(16, 185, 129, 0.9);
  color: #fff;
}

.card-badge.vip-badge {
  background: rgba(245, 158, 11, 0.9);
  color: #fff;
}

.card-type-tag {
  position: absolute;
  bottom: 10px;
  right: 10px;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  background: rgba(0,0,0,0.5);
  color: #fff;
}

.card-body {
  padding: 16px;
}

.card-name {
  font-size: 15px;
  font-weight: 500;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-meta {
  margin-bottom: 10px;
}

.card-time {
  font-size: 12px;
  color: #94a3b8;
}

.card-tag-row {
  display: flex;
  align-items: center;
}

.card-free-tag {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 4px;
  background: #ecfdf5;
  color: #059669;
  font-weight: 500;
}

.card-vip-tag {
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 4px;
  background: #fffbeb;
  color: #d97706;
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 0;
  color: #94a3b8;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.empty-state p {
  font-size: 14px;
}

/* 分页 */
.pagination {
  margin-top: 32px;
  display: flex;
  justify-content: center;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background: #10b981;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled):hover) {
  color: #10b981;
}

/* 响应式 */
@media (max-width: 900px) {
  .course-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .filter-bar {
    flex-direction: column;
  }
}

@media (max-width: 600px) {
  .course-page {
    padding: 16px;
  }

  .page-header h2 {
    font-size: 20px;
  }

  .course-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .filter-bar {
    flex-direction: column;
  }

  .filter-group {
    flex-wrap: wrap;
  }

  .filter-search {
    min-width: 100%;
  }

  .card-body {
    padding: 10px;
  }

  .card-name {
    font-size: 13px;
  }
}
</style>
