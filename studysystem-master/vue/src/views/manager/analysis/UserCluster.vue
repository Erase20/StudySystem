<template>
  <div class="main-content">
    <div style="margin-bottom: 20px;">
      <el-button type="primary" icon="el-icon-s-data" @click="performClustering" :loading="loading">
        执行K-Means聚类分析
      </el-button>
      <el-tag v-if="silhouetteScore !== null" style="margin-left: 15px;" type="success">
        轮廓系数: {{ silhouetteScore.toFixed(4) }}
      </el-tag>
      <el-tag v-if="userCount !== null" style="margin-left: 10px;" type="info">
        分析用户数: {{ userCount }}
      </el-tag>
    </div>

    <!-- 聚类分布统计 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6" v-for="(item, index) in clusterDistribution" :key="index">
        <el-card shadow="hover" :style="{ background: clusterColors[item.cluster_label] + '15', borderLeft: '4px solid ' + clusterColors[item.cluster_label] }">
          <div style="font-size: 14px; color: #666;">{{ clusterNames[item.cluster_label] }}</div>
          <div style="font-size: 28px; font-weight: bold; color: #333; margin-top: 5px;">{{ item.cnt }} 人</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="12">
        <el-card>
          <div slot="header">各群体人数分布</div>
          <div ref="barChart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div slot="header">群体特征雷达图</div>
          <div ref="radarChart" style="width: 100%; height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户列表 -->
    <el-card>
      <div slot="header">
        <span>聚类结果列表</span>
        <el-select v-model="filterLabel" placeholder="筛选群体" size="small" style="margin-left: 15px; width: 150px;" clearable @change="loadData">
          <el-option label="全部" value=""></el-option>
          <el-option v-for="(name, idx) in clusterNames" :key="idx" :label="name" :value="idx"></el-option>
        </el-select>
      </div>
      <el-table :data="clusterList" stripe>
        <el-table-column prop="userId" label="用户ID" width="80"></el-table-column>
        <el-table-column prop="userName" label="用户昵称">
          <template slot-scope="scope">
            <div style="display: flex; align-items: center;">
              <el-avatar :size="30" :src="scope.row.userAvatar" style="margin-right: 8px;"></el-avatar>
              <span>{{ scope.row.userName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="clusterName" label="所属群体">
          <template slot-scope="scope">
            <el-tag :color="clusterColors[scope.row.clusterLabel]" effect="dark" size="small">
              {{ scope.row.clusterName }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="featuresJson" label="特征向量" min-width="200">
          <template slot-scope="scope">
            <span style="font-size: 12px; color: #666;">{{ formatFeatures(scope.row.featuresJson) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="updateTime" label="分析时间" width="160"></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'UserCluster',

  data() {
    return {
      loading: false,
      silhouetteScore: null,
      userCount: null,
      clusterDistribution: [],
      clusterList: [],
      filterLabel: '',
      clusterNames: ['流失风险', '低活跃用户', '一般活跃用户', '高价值用户'],
      clusterColors: ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A'],
      barChartInstance: null,
      radarChartInstance: null,
      clusterCenters: []
    }
  },

  mounted() {
    this.loadDistribution()
    this.loadData()
  },

  beforeDestroy() {
    if (this.barChartInstance) this.barChartInstance.dispose()
    if (this.radarChartInstance) this.radarChartInstance.dispose()
  },

  methods: {
    performClustering() {
      this.loading = true
      this.$request.post('/userCluster/perform').then(res => {
        if (res.code === '200') {
          this.$message.success('K-Means聚类分析完成')
          this.silhouetteScore = res.data.silhouetteScore
          this.userCount = res.data.userCount
          this.clusterCenters = res.data.clusterCenters
          this.loadDistribution()
          this.loadData()
          this.renderCharts()
        } else {
          this.$message.error(res.msg)
        }
      }).catch(err => {
        this.$message.error('聚类分析失败：' + err.message)
      }).finally(() => {
        this.loading = false
      })
    },

    loadDistribution() {
      this.$request.get('/userCluster/distribution').then(res => {
        if (res.code === '200') {
          this.clusterDistribution = res.data
          this.renderBarChart()
        }
      })
    },

    loadData() {
      const params = {}
      if (this.filterLabel !== '') {
        params.clusterLabel = this.filterLabel
      }
      this.$request.get('/userCluster/selectAll', { params }).then(res => {
        if (res.code === '200') {
          this.clusterList = res.data
        }
      })
    },

    renderCharts() {
      this.renderBarChart()
      this.renderRadarChart()
    },

    renderBarChart() {
      if (!this.$refs.barChart) return
      if (this.barChartInstance) this.barChartInstance.dispose()

      this.barChartInstance = echarts.init(this.$refs.barChart)
      const data = this.clusterDistribution.map(item => ({
        name: this.clusterNames[item.cluster_label],
        value: item.cnt,
        label: item.cluster_label
      }))

      const option = {
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: data.map(d => d.name),
          axisLabel: { interval: 0 }
        },
        yAxis: { type: 'value', name: '人数' },
        series: [{
          type: 'bar',
          data: data.map(d => ({
            value: d.value,
            itemStyle: { color: this.clusterColors[d.label] }
          })),
          barWidth: '50%',
          label: { show: true, position: 'top' }
        }]
      }
      this.barChartInstance.setOption(option)
    },

    renderRadarChart() {
      if (!this.$refs.radarChart) return
      if (this.radarChartInstance) this.radarChartInstance.dispose()

      this.radarChartInstance = echarts.init(this.$refs.radarChart)

      const featureNames = ['购买课程数', '学习时长', '平均进度', '签到天数', '评论次数', '消费金额']
      const indicator = featureNames.map(name => ({ name, max: 1 }))

      const seriesData = this.clusterCenters.map((center, idx) => ({
        value: center,
        name: this.clusterNames[idx],
        itemStyle: { color: this.clusterColors[idx] },
        areaStyle: { opacity: 0.2 }
      }))

      const option = {
        tooltip: {},
        legend: {
          data: this.clusterNames,
          bottom: 0
        },
        radar: {
          indicator: indicator,
          shape: 'polygon',
          splitNumber: 4
        },
        series: [{
          type: 'radar',
          data: seriesData
        }]
      }
      this.radarChartInstance.setOption(option)
    },

    formatFeatures(jsonStr) {
      if (!jsonStr) return ''
      try {
        const obj = JSON.parse(jsonStr)
        return Object.entries(obj).map(([k, v]) => {
          const labels = {
            purchaseCount: '购买', totalLearnDuration: '时长',
            avgProgress: '进度', signinDays: '签到',
            commentCount: '评论', totalSpend: '消费'
          }
          return `${labels[k] || k}: ${typeof v === 'number' ? v.toFixed(1) : v}`
        }).join(' | ')
      } catch (e) {
        return jsonStr
      }
    }
  }
}
</script>

<style scoped>
.main-content {
  padding: 20px;
}
</style>
