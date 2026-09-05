<template>
  <div class="learning-center">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>学习中心</h2>
      <p>记录学习轨迹，规划学习路径，提升学习效率</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="section-title">
        <span class="title-icon">◆</span>
        <span>学习概览</span>
      </div>
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-value">{{ statistics.totalDuration || 0 }}</div>
          <div class="stat-label">学习时长(分钟)</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ statistics.totalCourses || 0 }}</div>
          <div class="stat-label">学习课程数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ notes.length }}</div>
          <div class="stat-label">笔记数量</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ user.score || 0 }}</div>
          <div class="stat-label">我的积分</div>
        </div>
      </div>
    </div>

    <div class="content-row">
      <!-- 左侧 -->
      <div class="left-column">
        <!-- 学习记录 -->
        <div class="section-card">
          <div class="section-title">
            <span class="title-icon">◆</span>
            <span>学习记录</span>
            <el-button type="text" class="clear-btn" @click="clearRecords">清空</el-button>
          </div>
          <div class="record-list">
            <div v-if="records.length === 0" class="empty-state">
              <p>暂无学习记录</p>
            </div>
            <div v-for="item in records" :key="item.id" class="record-item" @click="goToCourse(item.courseId)">
              <div class="record-icon">
                <i :class="item.courseType === 'VIDEO' ? 'el-icon-video-camera' : 'el-icon-document'"></i>
              </div>
              <div class="record-info">
                <div class="record-name">{{ item.courseName }}</div>
                <div class="record-meta">
                  <span class="meta-tag">{{ item.courseType === 'VIDEO' ? '视频' : '图文' }}</span>
                  <span>{{ item.duration }}分钟</span>
                </div>
              </div>
              <div class="record-progress">
                <el-progress :percentage="item.progress" :stroke-width="6" :show-text="false"></el-progress>
                <span class="progress-text">{{ item.progress }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 学习计划 -->
        <div class="section-card">
          <div class="section-title">
            <span class="title-icon">◆</span>
            <span>学习计划</span>
            <el-button type="primary" size="small" class="add-btn" @click="showPlanDialog">添加</el-button>
          </div>
          <div class="plan-list">
            <div v-if="plans.length === 0" class="empty-state">
              <p>暂无学习计划</p>
            </div>
            <div v-for="item in plans" :key="item.id" class="plan-item">
              <div class="plan-header">
                <span class="plan-title">{{ item.title }}</span>
                <span class="plan-status" :class="item.status">{{ item.status }}</span>
              </div>
              <div class="plan-content">{{ item.content }}</div>
              <div class="plan-meta">
                <span>每日 {{ item.dailyGoal }} 分钟</span>
                <span v-if="item.courseName">{{ item.courseName }}</span>
              </div>
              <div class="plan-progress">
                <el-progress :percentage="item.progress" :stroke-width="8"></el-progress>
              </div>
              <div class="plan-actions">
                <el-button type="text" size="mini" @click="editPlan(item)">编辑</el-button>
                <el-button type="text" size="mini" class="danger" @click="deletePlan(item.id)">删除</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧 -->
      <div class="right-column">
        <!-- 课堂笔记 -->
        <div class="section-card">
          <div class="section-title">
            <span class="title-icon">◆</span>
            <span>课堂笔记</span>
            <el-button type="primary" size="small" class="add-btn" @click="showNoteDialog">添加</el-button>
          </div>
          <div class="note-list">
            <div v-if="notes.length === 0" class="empty-state">
              <p>暂无笔记</p>
            </div>
            <div v-for="item in notes" :key="item.id" class="note-item">
              <div class="note-header">
                <span class="note-title">{{ item.title || '无标题' }}</span>
                <span class="note-course">{{ item.courseName }}</span>
              </div>
              <div class="note-content">{{ item.content }}</div>
              <div class="note-footer">
                <span class="note-time">{{ item.createTime }}</span>
                <div class="note-actions">
                  <el-button type="text" size="mini" @click="editNote(item)">编辑</el-button>
                  <el-button type="text" size="mini" class="danger" @click="deleteNote(item.id)">删除</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 积分排行榜 -->
        <div class="section-card rank-card">
          <div class="section-title">
            <span class="title-icon">◆</span>
            <span>积分排行榜</span>
          </div>
          <div class="rank-list">
            <div v-if="rankList.length === 0" class="empty-state">
              <p>暂无排行数据</p>
            </div>
            <div v-for="(item, index) in rankList" :key="item.id" class="rank-item">
              <div class="rank-medal" :class="'rank-' + (index + 1)">
                <span v-if="index < 3">★</span>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <img :src="$getImageUrl(item.avatar) || require('@/assets/imgs/logo.png')" class="rank-avatar">
              <div class="rank-info">
                <div class="rank-name">{{ item.name }}</div>
              </div>
              <div class="rank-score">{{ item.score }} 积分</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 弹窗 -->
    <el-dialog :title="planForm.id ? '编辑计划' : '添加计划'" :visible.sync="planDialogVisible" width="500px">
      <el-form :model="planForm" label-width="100px">
        <el-form-item label="计划标题">
          <el-input v-model="planForm.title" placeholder="请输入计划标题"></el-input>
        </el-form-item>
        <el-form-item label="计划内容">
          <el-input type="textarea" v-model="planForm.content" :rows="3"></el-input>
        </el-form-item>
        <el-form-item label="目标课程">
          <el-select v-model="planForm.targetCourseId" placeholder="选择目标课程" clearable style="width: 100%">
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="每日目标">
          <el-input-number v-model="planForm.dailyGoal" :min="10" :max="300" :step="10"></el-input-number>
          <span style="margin-left: 10px; color: #94a3b8;">分钟</span>
        </el-form-item>
        <el-form-item label="计划日期">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期" value-format="yyyy-MM-dd" style="width: 100%"></el-date-picker>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePlan">确定</el-button>
      </div>
    </el-dialog>

    <el-dialog :title="noteForm.id ? '编辑笔记' : '添加笔记'" :visible.sync="noteDialogVisible" width="600px">
      <el-form :model="noteForm" label-width="80px">
        <el-form-item label="关联课程">
          <el-select v-model="noteForm.courseId" placeholder="选择关联课程" clearable style="width: 100%">
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="笔记标题">
          <el-input v-model="noteForm.title" placeholder="请输入笔记标题"></el-input>
        </el-form-item>
        <el-form-item label="笔记内容">
          <el-input type="textarea" v-model="noteForm.content" :rows="6"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNote">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 学习中心页面
 */
export default {
  name: 'LearningCenter',
  
  data() {
    return {
      user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
      statistics: {},
      records: [],
      plans: [],
      notes: [],
      rankList: [],
      courses: [],
      planDialogVisible: false,
      noteDialogVisible: false,
      dateRange: [],
      planForm: { dailyGoal: 30 },
      noteForm: {}
    }
  },
  
  mounted() {
    this.loadAllData()
  },
  
  methods: {
    loadAllData() {
      this.loadStatistics()
      this.loadRecords()
      this.loadPlans()
      this.loadNotes()
      this.loadRankList()
      this.loadCourses()
    },
    
    loadStatistics() {
      this.$request.get('/learningRecord/statistics').then(res => {
        if (res.code === '200') this.statistics = res.data
      }).catch(() => {})
    },
    
    loadRecords() {
      this.$request.get('/learningRecord/selectByUser').then(res => {
        if (res.code === '200') this.records = res.data || []
      }).catch(() => {})
    },
    
    loadPlans() {
      this.$request.get('/learningPlan/selectByUser').then(res => {
        if (res.code === '200') this.plans = res.data || []
      }).catch(() => {})
    },
    
    loadNotes() {
      this.$request.get('/note/selectByUser').then(res => {
        if (res.code === '200') this.notes = res.data || []
      }).catch(() => {})
    },
    
    loadRankList() {
      this.$request.get('/user/scoreRank?limit=10').then(res => {
        if (res.code === '200') this.rankList = res.data || []
      }).catch(() => {})
    },
    
    loadCourses() {
      this.$request.get('/course/selectAll').then(res => {
        if (res.code === '200') this.courses = res.data || []
      }).catch(() => {})
    },
    
    goToCourse(id) {
      this.$router.push('/front/courseDetail?id=' + id)
    },
    
    showPlanDialog() {
      this.planForm = { dailyGoal: 30 }
      this.dateRange = []
      this.planDialogVisible = true
    },
    
    editPlan(item) {
      this.planForm = { ...item }
      this.dateRange = [item.startDate, item.endDate]
      this.planDialogVisible = true
    },
    
    savePlan() {
      if (this.dateRange && this.dateRange.length === 2) {
        this.planForm.startDate = this.dateRange[0]
        this.planForm.endDate = this.dateRange[1]
      }
      const url = this.planForm.id ? '/learningPlan/update' : '/learningPlan/add'
      this.$request.post(url, this.planForm).then(res => {
        if (res.code === '200') {
          this.$message.success('保存成功')
          this.planDialogVisible = false
          this.loadPlans()
        } else {
          this.$message.error(res.msg)
        }
      }).catch(() => {})
    },
    
    deletePlan(id) {
      this.$confirm('确定删除该计划?', '提示', { type: 'warning' }).then(() => {
        this.$request.delete('/learningPlan/delete/' + id).then(res => {
          if (res.code === '200') {
            this.$message.success('删除成功')
            this.loadPlans()
          }
        }).catch(() => {})
      }).catch(() => {})
    },
    
    showNoteDialog() {
      this.noteForm = {}
      this.noteDialogVisible = true
    },
    
    editNote(item) {
      this.noteForm = { ...item }
      this.noteDialogVisible = true
    },
    
    saveNote() {
      const url = this.noteForm.id ? '/note/update' : '/note/add'
      this.$request.post(url, this.noteForm).then(res => {
        if (res.code === '200') {
          this.$message.success('保存成功')
          this.noteDialogVisible = false
          this.loadNotes()
        } else {
          this.$message.error(res.msg)
        }
      }).catch(() => {})
    },
    
    deleteNote(id) {
      this.$confirm('确定删除该笔记?', '提示', { type: 'warning' }).then(() => {
        this.$request.delete('/note/delete/' + id).then(res => {
          if (res.code === '200') {
            this.$message.success('删除成功')
            this.loadNotes()
          }
        }).catch(() => {})
      }).catch(() => {})
    },
    
    clearRecords() {
      this.$confirm('确定清空所有学习记录?', '提示', { type: 'warning' }).then(() => {
        this.records.forEach(r => {
          this.$request.delete('/learningRecord/delete/' + r.id)
        })
        setTimeout(() => {
          this.loadRecords()
          this.loadStatistics()
          this.$message.success('已清空')
        }, 500)
      }).catch(() => {})
    }
  }
}
</script>

<style scoped>
.learning-center {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

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

.clear-btn,
.add-btn {
  margin-left: auto;
  font-size: 13px;
}

.add-btn {
  background: #1e293b !important;
  border-color: #1e293b !important;
}

.clear-btn {
  color: #94a3b8 !important;
}

.clear-btn:hover {
  color: #ef4444 !important;
}

.stats-section {
  margin-bottom: 32px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
}

.content-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
}

.empty-state p {
  font-size: 14px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.record-item:hover {
  background: #f8fafc;
}

.record-icon {
  width: 40px;
  height: 40px;
  background: #f1f5f9;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #475569;
}

.record-info {
  flex: 1;
}

.record-name {
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 4px;
}

.record-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #94a3b8;
}

.meta-tag {
  background: #f1f5f9;
  color: #475569;
  padding: 2px 6px;
  border-radius: 4px;
}

.record-progress {
  width: 80px;
  text-align: right;
}

.progress-text {
  font-size: 11px;
  color: #94a3b8;
  margin-left: 4px;
}

.plan-item {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  margin-bottom: 12px;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.plan-title {
  font-weight: 600;
  color: #1e293b;
}

.plan-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f1f5f9;
  color: #64748b;
}

.plan-status.已完成,
.plan-status.进行中 {
  background: #1e293b;
  color: #fff;
}

.plan-content {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.plan-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 12px;
}

.plan-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.note-item {
  padding: 16px 0;
  border-bottom: 1px solid #f1f5f9;
}

.note-item:last-child {
  border-bottom: none;
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.note-title {
  font-weight: 500;
  color: #1e293b;
}

.note-course {
  font-size: 11px;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
}

.note-content {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 8px;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.note-time {
  font-size: 12px;
  color: #94a3b8;
}

.note-actions .danger {
  color: #ef4444 !important;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  transition: background 0.3s;
}

.rank-item:hover {
  background: #f8fafc;
}

.rank-medal {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-right: 12px;
  background: #f1f5f9;
  color: #64748b;
}

.rank-medal.rank-1 {
  background: #1e293b;
  color: #fff;
}

.rank-medal.rank-2 {
  background: #475569;
  color: #fff;
}

.rank-medal.rank-3 {
  background: #64748b;
  color: #fff;
}

.rank-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  margin-right: 12px;
  border: 1px solid #e2e8f0;
}

.rank-info {
  flex: 1;
}

.rank-name {
  font-weight: 500;
  color: #1e293b;
}

.rank-score {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

@media (max-width: 1024px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .content-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .learning-center {
    padding: 16px;
  }

  .page-header h2 {
    font-size: 20px;
  }

  .stats-row {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }

  .stat-card {
    padding: 14px;
  }

  .stat-value {
    font-size: 22px;
  }

  .record-progress {
    display: none;
  }

  .plan-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
