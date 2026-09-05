<template>
  <div class="main-content">
    <div style="margin-bottom: 20px;">
      <el-button type="primary" icon="el-icon-chat-dot-round" @click="analyzeAll" :loading="loading">
        执行评论情感分析
      </el-button>
      <el-tag v-if="totalCount !== null" style="margin-left: 15px;" type="info">
        分析评论数: {{ totalCount }}
      </el-tag>
      <el-tag v-if="positiveRate" style="margin-left: 10px;" type="success">
        正面: {{ positiveRate }}
      </el-tag>
      <el-tag v-if="negativeRate" style="margin-left: 10px;" type="danger">
        负面: {{ negativeRate }}
      </el-tag>
    </div>

    <!-- 情感分布统计 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card shadow="hover" style="border-left: 4px solid #67C23A;">
          <div style="font-size: 14px; color: #666;">正面评论</div>
          <div style="font-size: 28px; font-weight: bold; color: #67C23A; margin-top: 5px;">{{ sentimentCount.positive || 0 }} 条</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" style="border-left: 4px solid #909399;">
          <div style="font-size: 14px; color: #666;">中性评论</div>
          <div style="font-size: 28px; font-weight: bold; color: #909399; margin-top: 5px;">{{ sentimentCount.neutral || 0 }} 条</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover" style="border-left: 4px solid #F56C6C;">
          <div style="font-size: 14px; color: #666;">负面评论</div>
          <div style="font-size: 28px; font-weight: bold; color: #F56C6C; margin-top: 5px;">{{ sentimentCount.negative || 0 }} 条</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card>
          <div slot="header">情感分布</div>
          <div ref="pieChart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header">课程情感评分TOP10</div>
          <div style="max-height: 350px; overflow-y: auto;">
            <el-table :data="courseRank" size="small" stripe>
              <el-table-column type="index" label="排名" width="50"></el-table-column>
              <el-table-column prop="courseName" label="课程名称" show-overflow-tooltip></el-table-column>
              <el-table-column prop="commentCount" label="评论数" width="80"></el-table-column>
              <el-table-column prop="avgScore" label="情感分" width="80">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.avgScore > 0.2 ? 'success' : scope.row.avgScore < -0.2 ? 'danger' : 'info'" size="mini">
                    {{ scope.row.avgScore }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 评论列表 -->
    <el-card>
      <div slot="header">
        <span>评论情感分析结果</span>
        <el-select v-model="filterLabel" placeholder="筛选情感" size="small" style="margin-left: 15px; width: 150px;" clearable @change="loadData">
          <el-option label="全部" value=""></el-option>
          <el-option label="正面" value="正面"></el-option>
          <el-option label="中性" value="中性"></el-option>
          <el-option label="负面" value="负面"></el-option>
        </el-select>
      </div>
      <el-table :data="sentimentList" stripe>
        <el-table-column prop="commentId" label="评论ID" width="80"></el-table-column>
        <el-table-column prop="userName" label="用户" width="100"></el-table-column>
        <el-table-column prop="courseName" label="课程" width="150" show-overflow-tooltip></el-table-column>
        <el-table-column prop="commentContent" label="评论内容" min-width="250" show-overflow-tooltip>
          <template slot-scope="scope">
            <span v-html="scope.row.commentContent"></span>
          </template>
        </el-table-column>
        <el-table-column prop="sentimentLabel" label="情感倾向" width="90">
          <template slot-scope="scope">
            <el-tag :type="scope.row.sentimentLabel === '正面' ? 'success' : scope.row.sentimentLabel === '负面' ? 'danger' : 'info'" size="small">
              {{ scope.row.sentimentLabel }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sentimentScore" label="情感得分" width="90">
          <template slot-scope="scope">
            <span :style="{ color: scope.row.sentimentScore > 0 ? '#67C23A' : scope.row.sentimentScore < 0 ? '#F56C6C' : '#909399' }">
              {{ scope.row.sentimentScore ? scope.row.sentimentScore.toFixed(3) : 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="positiveWords" label="正面词" min-width="120" show-overflow-tooltip></el-table-column>
        <el-table-column prop="negativeWords" label="负面词" min-width="120" show-overflow-tooltip></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'SentimentAnalysis',

  data() {
    return {
      loading: false,
      totalCount: null,
      positiveRate: null,
      negativeRate: null,
      neutralRate: null,
      sentimentCount: {},
      sentimentList: [],
      courseRank: [],
      filterLabel: '',
      pieChartInstance: null
    }
  },

  mounted() {
    this.loadDistribution()
    this.loadData()
    this.loadCourseRank()
  },

  beforeDestroy() {
    if (this.pieChartInstance) this.pieChartInstance.dispose()
  },

  methods: {
    analyzeAll() {
      this.loading = true
      this.$request.post('/sentiment/analyze').then(res => {
        if (res.code === '200') {
          this.$message.success('评论情感分析完成')
          this.totalCount = res.data.totalCount
          this.positiveRate = res.data.positiveRate
          this.negativeRate = res.data.negativeRate
          this.neutralRate = res.data.neutralRate
          this.loadDistribution()
          this.loadData()
          this.loadCourseRank()
        } else {
          this.$message.error(res.msg)
        }
      }).catch(err => {
        this.$message.error('情感分析失败：' + err.message)
      }).finally(() => {
        this.loading = false
      })
    },

    loadDistribution() {
      this.$request.get('/sentiment/distribution').then(res => {
        if (res.code === '200') {
          const countMap = {}
          res.data.forEach(item => {
            const key = item.sentiment_label === '正面' ? 'positive' :
                        item.sentiment_label === '负面' ? 'negative' : 'neutral'
            countMap[key] = item.cnt
          })
          this.sentimentCount = countMap
          this.renderPieChart(res.data)
        }
      })
    },

    loadData() {
      const params = {}
      if (this.filterLabel) {
        params.sentimentLabel = this.filterLabel
      }
      this.$request.get('/sentiment/selectAll', { params }).then(res => {
        if (res.code === '200') {
          this.sentimentList = res.data
        }
      })
    },

    loadCourseRank() {
      this.$request.get('/sentiment/courseRank', { params: { limit: 10 } }).then(res => {
        if (res.code === '200') {
          this.courseRank = res.data
        }
      })
    },

    renderPieChart(data) {
      if (!this.$refs.pieChart) return
      if (this.pieChartInstance) this.pieChartInstance.dispose()

      this.pieChartInstance = echarts.init(this.$refs.pieChart)

      const colorMap = { '正面': '#67C23A', '中性': '#909399', '负面': '#F56C6C' }
      const option = {
        tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} ({d}%)' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{
          name: '情感分布',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          label: { show: true, formatter: '{b}: {c}' },
          data: data.map(item => ({
            value: item.cnt,
            name: item.sentiment_label,
            itemStyle: { color: colorMap[item.sentiment_label] || '#409EFF' }
          }))
        }]
      }
      this.pieChartInstance.setOption(option)
    }
  }
}
</script>

<style scoped>
.main-content {
  padding: 20px;
}
</style>
