<template>
  <div class="dashboard">
    <!-- 欢迎栏 -->
    <div class="welcome-bar">
      <div class="welcome-info">
        <h2>您好，{{ user?.name || '管理员' }}！</h2>
        <p>欢迎回来，祝您工作愉快</p>
      </div>
      <div class="welcome-date">
        <i class="el-icon-date"></i>
        <span>{{ currentDate }}</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card" v-for="item in statCards" :key="item.key">
        <div class="stat-icon" :style="{ background: item.color }">
          <i :class="item.icon"></i>
        </div>
        <div class="stat-detail">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <!-- 图表行 -->
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-header">
          <h3>订单分类</h3>
        </div>
        <div class="chart-body" id="coursePie"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>用户角色</h3>
        </div>
        <div class="chart-body" id="userPie"></div>
      </div>
    </div>

    <!-- 柱状图 -->
    <div class="chart-full">
      <div class="chart-header">
        <h3>数据统计</h3>
      </div>
      <div class="chart-body-lg" id="bar"></div>
    </div>

    <!-- 底部双栏 -->
    <div class="bottom-row">
      <div class="chart-card">
        <div class="chart-header">
          <h3>最新公告</h3>
          <span class="chart-more" @click="$router.push('/notice')">查看全部</span>
        </div>
        <div class="notice-list">
          <div class="notice-item" v-for="item in notices.slice(0, 5)" :key="item.id">
            <div class="notice-dot"></div>
            <div class="notice-content">
              <span class="notice-title">{{ item.title }}</span>
              <span class="notice-time">{{ item.time }}</span>
            </div>
          </div>
          <div class="notice-empty" v-if="!notices.length">暂无公告</div>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <h3>快捷操作</h3>
        </div>
        <div class="quick-actions">
          <div class="action-item" @click="$router.push('/course')">
            <i class="el-icon-video-camera"></i>
            <span>课程管理</span>
          </div>
          <div class="action-item" @click="$router.push('/orders')">
            <i class="el-icon-shopping-cart-2"></i>
            <span>课程订单</span>
          </div>
          <div class="action-item" @click="$router.push('/user')">
            <i class="el-icon-user"></i>
            <span>用户管理</span>
          </div>
          <div class="action-item" @click="$router.push('/notice')">
            <i class="el-icon-bell"></i>
            <span>公告管理</span>
          </div>
          <div class="action-item" @click="$router.push('/information')">
            <i class="el-icon-document"></i>
            <span>资料审核</span>
          </div>
          <div class="action-item" @click="$router.push('/score')">
            <i class="el-icon-trophy"></i>
            <span>积分专区</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from "echarts";

export default {
  name: 'Home',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
      notices: [],
      statCards: [
        { key: 'users', label: '注册用户', value: '--', icon: 'el-icon-user', color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
        { key: 'courses', label: '课程总数', value: '--', icon: 'el-icon-reading', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
        { key: 'orders', label: '订单总数', value: '--', icon: 'el-icon-s-order', color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
        { key: 'info', label: '学习资料', value: '--', icon: 'el-icon-document', color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' },
      ],
      chartInstances: []
    }
  },
  computed: {
    currentDate() {
      const d = new Date()
      const week = ['日', '一', '二', '三', '四', '五', '六']
      return d.getFullYear() + '年' + (d.getMonth() + 1) + '月' + d.getDate() + '日 星期' + week[d.getDay()]
    }
  },
  mounted() {
    this.loadNotice()
    this.loadStats()
    this.loadCourseOption()
    this.loadUserOption()
    this.loadBar()
    window.addEventListener('resize', this.handleResize)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
    this.chartInstances.forEach(c => c && c.dispose())
  },
  methods: {
    handleResize() {
      this.chartInstances.forEach(c => c && c.resize())
    },
    initChart(domId) {
      const dom = document.getElementById(domId)
      if (!dom) return null
      const chart = echarts.init(dom)
      this.chartInstances.push(chart)
      return chart
    },
    loadNotice() {
      this.$request.get('/notice/selectAll').then(res => {
        this.notices = res.data || []
      }).catch(() => {})
    },
    loadStats() {
      // 用户总数
      this.$request.get('/user/selectPage', { params: { pageNum: 1, pageSize: 1 } }).then(res => {
        this.updateStat('users', res.data?.total || 0)
      }).catch(() => {})
      // 课程总数
      this.$request.get('/course/selectPage', { params: { pageNum: 1, pageSize: 1 } }).then(res => {
        this.updateStat('courses', res.data?.total || 0)
      }).catch(() => {})
      // 订单总数
      this.$request.get('/orders/selectPage', { params: { pageNum: 1, pageSize: 1 } }).then(res => {
        this.updateStat('orders', res.data?.total || 0)
      }).catch(() => {})
      // 资料总数
      this.$request.get('/information/selectPage', { params: { pageNum: 1, pageSize: 1 } }).then(res => {
        this.updateStat('info', res.data?.total || 0)
      }).catch(() => {})
    },
    updateStat(key, value) {
      const card = this.statCards.find(c => c.key === key)
      if (card) this.$set(card, 'value', value)
    },
    loadBar() {
      this.$request.get('/getBar').then(res => {
        if (res.code === '200') {
          const myChart = this.initChart('bar')
          if (!myChart) return
          myChart.setOption({
            title: { text: res.data.text || '', subtext: res.data.subText || '', left: 'center', textStyle: { fontSize: 14, color: '#333' } },
            tooltip: { trigger: 'axis' },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
            xAxis: { type: 'category', data: res.data.xAxis || [], axisLine: { lineStyle: { color: '#ddd' } }, axisLabel: { color: '#666' } },
            yAxis: { type: 'value', axisLine: { show: false }, axisLabel: { color: '#666' }, splitLine: { lineStyle: { type: 'dashed' } } },
            series: [{
              data: res.data.yAxis || [],
              type: 'bar',
              barWidth: '40%',
              itemStyle: {
                borderRadius: [4, 4, 0, 0],
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: '#4facfe' },
                  { offset: 1, color: '#00f2fe' }
                ])
              }
            }]
          })
        }
      }).catch(() => {})
    },
    loadUserOption() {
      this.$request.get('/user/getPie').then(res => {
        if (res.code === '200') {
          const myChart = this.initChart('userPie')
          if (!myChart) return
          myChart.setOption({
            title: { text: res.data.text || '', subtext: res.data.subText || '', left: 'center', textStyle: { fontSize: 14, color: '#333' } },
            tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
            legend: { orient: 'vertical', left: 'left', top: 'middle', textStyle: { color: '#666' } },
            series: [{
              name: res.data.name || '',
              type: 'pie',
              radius: ['40%', '65%'],
              center: ['60%', '55%'],
              data: res.data.data || [],
              label: { show: false },
              emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
              itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 }
            }]
          })
        }
      }).catch(() => {})
    },
    loadCourseOption() {
      this.$request.get('/orders/getPie').then(res => {
        if (res.code === '200') {
          const myChart = this.initChart('coursePie')
          if (!myChart) return
          myChart.setOption({
            title: { text: res.data.text || '', subtext: res.data.subText || '', left: 'center', textStyle: { fontSize: 14, color: '#333' } },
            tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
            legend: { orient: 'vertical', left: 'left', top: 'middle', textStyle: { color: '#666' } },
            series: [{
              name: res.data.name || '',
              type: 'pie',
              radius: ['40%', '65%'],
              center: ['60%', '55%'],
              data: res.data.data || [],
              label: { show: false },
              emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
              itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 }
            }]
          })
        }
      }).catch(() => {})
    }
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 欢迎栏 */
.welcome-bar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  padding: 24px 28px;
  color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-bar h2 {
  margin: 0 0 6px 0;
  font-size: 20px;
  font-weight: 600;
}

.welcome-bar p {
  margin: 0;
  font-size: 13px;
  opacity: 0.85;
}

.welcome-date {
  font-size: 14px;
  opacity: 0.9;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* 统计卡片 */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 10px 0 rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  flex-shrink: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 2px;
}

/* 图表行 */
.chart-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-full {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px 0 rgba(0, 0, 0, 0.08);
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px 0 rgba(0, 0, 0, 0.08);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chart-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.chart-more {
  font-size: 13px;
  color: #409EFF;
  cursor: pointer;
}

.chart-more:hover {
  color: #66b1ff;
}

.chart-body {
  height: 300px;
}

.chart-body-lg {
  height: 350px;
}

/* 底部双栏 */
.bottom-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

/* 公告列表 */
.notice-list {
  max-height: 280px;
  overflow-y: auto;
}

.notice-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.notice-item:last-child {
  border-bottom: none;
}

.notice-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #409EFF;
  margin-top: 7px;
  flex-shrink: 0;
}

.notice-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notice-title {
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 60%;
}

.notice-time {
  font-size: 12px;
  color: #94a3b8;
  flex-shrink: 0;
}

.notice-empty {
  padding: 40px 0;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}

/* 快捷操作 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 12px;
  border-radius: 8px;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s;
}

.action-item:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
}

.action-item i {
  font-size: 22px;
  color: #64748b;
}

.action-item span {
  font-size: 13px;
  color: #475569;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stat-cards {
    grid-template-columns: 1fr 1fr;
  }
  .chart-row {
    grid-template-columns: 1fr;
  }
  .bottom-row {
    grid-template-columns: 1fr;
  }
  .quick-actions {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 480px) {
  .stat-cards {
    grid-template-columns: 1fr;
  }
  .welcome-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
