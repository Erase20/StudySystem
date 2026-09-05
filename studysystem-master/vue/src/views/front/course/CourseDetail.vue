<template>
  <div class="course-detail-page">
    <div class="video-learning-layout">
      <!-- 左侧：视频+内容 -->
      <div class="video-main-area">
        <div class="video-player-section">
          <div class="video-container">
            <div class="current-chapter-bar" v-if="currentChapter">
              <span class="chapter-playing"><i class="el-icon-video-play"></i> 正在播放</span>
              <span class="chapter-title">{{ currentChapter.title }}</span>
              <span class="chapter-category" v-if="courseData.category">{{ courseData.category }}</span>
            </div>
            <div v-if="canAccessVideo && currentVideoUrl" class="video-wrapper">
              <video ref="videoPlayer" :src="currentVideoUrl" controls class="course-video" @ended="onVideoEnded"></video>
            </div>
            <div v-else-if="canAccessVideo && !currentVideoUrl" class="video-wrapper no-video">
              <i class="el-icon-video-camera" style="font-size: 48px; color: #c0c4cc;"></i>
              <p style="color: #909399; margin-top: 10px;">该章节暂无视频资源</p>
            </div>
            <div v-else class="video-locked">
              <div class="lock-overlay">
                <div class="lock-icon-wrap"><i class="el-icon-lock"></i></div>
                <p>VIP专属内容，开通会员即可学习</p>
                <el-button class="buy-btn" @click="buy"><i class="el-icon-star-on"></i> 开通会员</el-button>
              </div>
            </div>
          </div>
        </div>
        <div class="content-tabs">
          <div class="tab-nav">
            <div class="tab-item" :class="{ active: activeTab === 'intro' }" @click="activeTab = 'intro'"><i class="el-icon-document"></i> 课程介绍</div>
            <div class="tab-item" :class="{ active: activeTab === 'comment' }" @click="activeTab = 'comment'"><i class="el-icon-chat-dot-round"></i> 学员评价 <span class="tab-badge" v-if="commentData.length">{{ commentData.length }}</span></div>
          </div>
          <div class="tab-content" v-show="activeTab === 'intro'">
            <div v-html="courseData.content || '<p style=color:#94a3b8>暂无课程介绍</p>'" class="course-content w-e-text w-e-text-container"></div>
            <div class="file-link" v-if="courseData.file"><i class="el-icon-link"></i><span>资料链接：</span><a :href="courseData.file" target="_blank">{{ courseData.file }}</a></div>
          </div>
          <div class="tab-content" v-show="activeTab === 'comment'">
            <div class="comment-form">
              <el-input type="textarea" :rows="4" v-model="content" placeholder="发表您对课程的看法..." class="comment-input"></el-input>
              <el-button type="primary" class="submit-btn" @click="submit(content, 0)"><i class="el-icon-s-promotion"></i> 发表评论</el-button>
            </div>
            <div class="comment-list">
              <div class="comment-item" v-for="item in commentData" :key="item.id">
                <div class="comment-avatar"><img :src="item.userAvatar" alt=""></div>
                <div class="comment-body">
                  <div class="comment-header"><span class="comment-username">{{ item.userName }}</span><span class="comment-time">{{ item.time }}</span></div>
                  <p class="comment-content">{{ item.content }}</p>
                  <div class="child-comments" v-if="item.children && item.children.length">
                    <div class="child-comment" v-for="child in item.children" :key="child.id">
                      <img :src="child.userAvatar" class="child-avatar">
                      <div class="child-body"><span class="child-username">{{ child.userName }}</span><span class="child-text">{{ child.content }}</span><span class="child-time">{{ child.time }}</span></div>
                    </div>
                  </div>
                  <div class="reply-form">
                    <el-input v-model="item.tmp" placeholder="写下你的回复..." class="reply-input"></el-input>
                    <el-button type="primary" size="small" @click="submit(item.tmp, item.id)">回复</el-button>
                  </div>
                </div>
              </div>
              <div class="no-comment" v-if="!commentData.length"><i class="el-icon-chat-line-round"></i><p>暂无评论，来发表第一条吧</p></div>
            </div>
          </div>
        </div>
      </div>
      <!-- 右侧：章节目录 -->
      <div class="chapter-sidebar">
        <div class="chapter-panel">
          <div class="chapter-panel-header">
            <h3><i class="el-icon-notebook-2"></i> 课程目录</h3>
            <span class="chapter-total">{{ chapterList.length }} 课时</span>
          </div>
          <div class="chapter-list">
            <div class="chapter-group" v-for="(group, gIdx) in groupedChapters" :key="gIdx">
              <div class="chapter-group-title" @click="toggleGroup(gIdx)">
                <i :class="group.collapsed ? 'el-icon-arrow-right' : 'el-icon-arrow-down'"></i>
                {{ group.name }}
                <span class="group-count">{{ group.items.length }} 课时</span>
              </div>
              <template v-if="!group.collapsed">
                <div class="chapter-item" v-for="ch in group.items" :key="ch.id" :class="{ active: currentChapter && currentChapter.id === ch.id }" @click="selectChapter(ch)">
                  <div class="chapter-item-left">
                    <i class="el-icon-video-play chapter-play-icon"></i>
                    <span class="chapter-item-title">{{ ch.title }}</span>
                  </div>
                  <div class="chapter-item-right">
                    <span class="chapter-duration" v-if="ch.duration">{{ formatDuration(ch.duration) }}</span>
                    <el-tag v-if="ch.freePreview" type="success" size="mini" effect="plain">试看</el-tag>
                    <i class="el-icon-lock chapter-lock-icon" v-if="!canAccessChapter(ch)"></i>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
        <div class="course-info-mini">
          <div class="info-row" v-if="courseData.category"><i class="el-icon-collection-tag"></i> <span>{{ courseData.category }}</span></div>
          <div class="info-row"><i class="el-icon-user"></i> <span>{{ learnerCount }} 人已学习</span></div>
          <div class="info-row">
            <i class="el-icon-unlock" v-if="!courseData.price || courseData.price === 0"></i>
            <i class="el-icon-star-on" v-else></i>
            <span v-if="!courseData.price || courseData.price === 0">免费开放</span>
            <span v-else>VIP课程</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    let courseId = this.$route.query.id
    return {
      user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
      courseId: courseId,
      courseData: {},
      flag: false,
      content: null,
      commentData: [],
      learnerCount: 0,
      chapterList: [],
      currentChapter: null,
      activeTab: 'intro',
      collapsedGroups: {}
    }
  },
  computed: {
    canAccessVideo() {
      return !this.courseData.price || this.courseData.price === 0 || this.flag
    },
    currentVideoUrl() {
      if (!this.currentChapter || !this.currentChapter.video) return ''
      const url = this.currentChapter.video
      if (url.startsWith('http://') || url.startsWith('https://')) return url
      if (url.startsWith('/files/')) return this.$baseUrl + url
      return this.$baseUrl + '/files/' + url
    },
    groupedChapters() {
      const groups = []
      const map = {}
      this.chapterList.forEach(ch => {
        const prefix = ch.title.split('-')[0] || '1'
        const chapterNum = prefix.trim()
        if (!map[chapterNum]) {
          map[chapterNum] = { name: '第' + chapterNum + '章', items: [], collapsed: !!this.collapsedGroups[chapterNum] }
          groups.push(map[chapterNum])
        }
        map[chapterNum].items.push(ch)
      })
      return groups
    }
  },
  mounted() {
    this.loadCourse()
    this.checkCourse()
    this.loadComment()
    this.loadLearnerCount()
  },
  methods: {
    loadCourse() {
      this.$request.get('/course/selectById/' + this.courseId).then(res => {
        if (res.code === '200') {
          this.courseData = res.data
          this.loadChapters()
          this.loadRelatedCourses()
        } else {
          this.$message.error(res.msg)
        }
      })
    },
    loadChapters() {
      this.$request.get('/chapter/course/' + this.courseId).then(res => {
        if (res.code === '200') {
          this.chapterList = res.data || []
          if (this.chapterList.length && !this.currentChapter) {
            const first = this.chapterList.find(ch => this.canAccessChapter(ch)) || this.chapterList[0]
            this.selectChapter(first)
          }
        }
      }).catch(() => {})
    },
    selectChapter(ch) {
      if (!this.canAccessChapter(ch)) {
        this.$message.warning('该章节为VIP内容，请先开通会员')
        return
      }
      this.currentChapter = ch
      const videoEl = document.querySelector('.video-player-section')
      if (videoEl) videoEl.scrollIntoView({ behavior: 'smooth', block: 'start' })
    },
    canAccessChapter(ch) {
      if (ch.freePreview) return true
      if (!this.courseData.price || this.courseData.price === 0) return true
      return this.flag
    },
    toggleGroup(gIdx) {
      const group = this.groupedChapters[gIdx]
      if (!group) return
      const prefix = group.name.replace('第', '').replace('章', '').trim()
      this.$set(this.collapsedGroups, prefix, !this.collapsedGroups[prefix])
      this.collapsedGroups = Object.assign({}, this.collapsedGroups)
    },
    formatDuration(seconds) {
      if (!seconds) return ''
      const m = Math.floor(seconds / 60)
      const s = seconds % 60
      return m + ':' + (s < 10 ? '0' : '') + s
    },
    onVideoEnded() {
      if (!this.currentChapter) return
      const idx = this.chapterList.findIndex(ch => ch.id === this.currentChapter.id)
      if (idx >= 0 && idx < this.chapterList.length - 1) {
        const next = this.chapterList[idx + 1]
        if (this.canAccessChapter(next)) this.selectChapter(next)
      }
    },
    checkCourse() {
      this.$request.get('/orders/selectAll', { params: { userId: this.user.id, courseId: this.courseId } }).then(res => {
        if (res.code === '200' && res.data.length > 0) this.flag = true
      })
    },
    loadRelatedCourses() {
      this.$request.get('/course/selectTop8?type=VIDEO').then(res => {
        if (res.code === '200') {
          // 优先推荐同分类课程
          let courses = (res.data || []).filter(c => c.id !== parseInt(this.courseId))
          if (this.courseData.category) {
            const sameCategory = courses.filter(c => c.category === this.courseData.category)
            const diffCategory = courses.filter(c => c.category !== this.courseData.category)
            courses = [...sameCategory, ...diffCategory]
          }
          this.relatedCourses = courses.slice(0, 4)
        }
      }).catch(() => {})
    },
    loadLearnerCount() {
      this.$request.get('/orders/selectAll', { params: { courseId: this.courseId } }).then(res => {
        if (res.code === '200') this.learnerCount = (res.data || []).length
      }).catch(() => {})
    },
    goRelated(id) {
      this.$router.push({ path: '/front/courseDetail', query: { id } })
      this.courseId = id
      this.currentChapter = null
      this.chapterList = []
      this.activeTab = 'intro'
      this.loadCourse()
      this.checkCourse()
      this.loadComment()
      this.loadLearnerCount()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    buy() {
      this.$request.post('/orders/add', { courseId: this.courseId, userId: this.user.id }).then(res => {
        if (res.code === '200') {
          this.$message.success('已解锁课程')
          this.loadCourse()
          this.checkCourse()
        } else {
          this.$message.error(res.msg)
        }
      })
    },
    submit(content, parentId) {
      this.$request.post('/comment/add', { userId: this.user.id, courseId: this.courseId, content: content, parentId: parentId }).then(res => {
        if (res.code === '200') {
          this.$message.success('评论成功')
          this.content = null
          this.loadComment()
        } else {
          this.$message.error(res.msg)
        }
      })
    },
    loadComment() {
      this.$request.get('/comment/selectAll', { params: { courseId: this.courseId } }).then(res => {
        if (res.code === '200') this.commentData = res.data
      })
    },
    getImageUrl(img) {
      if (!img) return require('@/assets/imgs/logo.png')
      return this.$getImageUrl(img)
    },
    handleImgError(e) {
      e.target.src = require('@/assets/imgs/logo.png')
    }
  }
}
</script>

<style scoped>
.course-detail-page { background: #f8fafc; min-height: 100vh; }
.video-learning-layout { display: flex; max-width: 1400px; margin: 0 auto; min-height: 100vh; }
.video-main-area { flex: 1; min-width: 0; background: #1e293b; }
.video-player-section { background: #000; }
.video-container { max-width: 960px; margin: 0 auto; }

.current-chapter-bar { display: flex; align-items: center; gap: 12px; padding: 12px 20px; background: rgba(0,0,0,0.6); color: #e2e8f0; font-size: 14px; }
.chapter-playing { color: #34d399; font-weight: 500; display: flex; align-items: center; gap: 4px; }
.chapter-title { color: #cbd5e1; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chapter-category { color: #60a5fa; font-size: 12px; padding: 2px 8px; background: rgba(96,165,250,0.15); border-radius: 10px; }

.video-wrapper { background: #000; position: relative; }
.course-video { width: 100%; max-height: 540px; display: block; }
.video-wrapper.no-video { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; background: #1a1a2e; }
.video-locked { min-height: 400px; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }
.lock-overlay { text-align: center; color: #e2e8f0; }
.lock-icon-wrap { width: 80px; height: 80px; background: rgba(255,255,255,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; }
.lock-icon-wrap i { font-size: 36px; color: #94a3b8; }
.lock-overlay p { font-size: 16px; color: #94a3b8; margin-bottom: 20px; }
.buy-btn { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important; border: none !important; padding: 12px 32px !important; font-size: 16px !important; border-radius: 10px !important; box-shadow: 0 4px 12px rgba(245,158,11,0.3) !important; }
.buy-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(245,158,11,0.4) !important; }

.content-tabs { background: #fff; min-height: 400px; }
.tab-nav { display: flex; border-bottom: 2px solid #f1f5f9; padding: 0 24px; }
.tab-item { padding: 16px 24px; font-size: 15px; font-weight: 500; color: #64748b; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }
.tab-item:hover { color: #2563eb; }
.tab-item.active { color: #2563eb; border-bottom-color: #2563eb; }
.tab-badge { background: #ef4444; color: #fff; font-size: 11px; padding: 1px 6px; border-radius: 10px; margin-left: 4px; }
.tab-content { padding: 24px; }
.course-content { line-height: 1.8; color: #475569; }
.file-link { padding: 16px; background: #f8fafc; border-radius: 8px; font-size: 14px; color: #64748b; margin-top: 16px; }
.file-link a { color: #2563eb; word-break: break-all; }
.file-link a:hover { text-decoration: underline; }

.comment-form { margin-bottom: 32px; }
.comment-input { margin-bottom: 16px; }
.comment-input :deep(.el-textarea__inner) { border-radius: 12px; border: 2px solid #e2e8f0; padding: 16px; font-size: 15px; }
.comment-input :deep(.el-textarea__inner:focus) { border-color: #2563eb; }
.submit-btn { background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important; border: none !important; padding: 10px 24px !important; border-radius: 8px !important; }
.comment-list { border-top: 1px solid #f1f5f9; padding-top: 24px; }
.comment-item { display: flex; gap: 16px; padding: 20px 0; border-bottom: 1px solid #f1f5f9; }
.comment-item:last-child { border-bottom: none; }
.comment-avatar img { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; }
.comment-body { flex: 1; }
.comment-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.comment-username { font-weight: 600; color: #1e293b; }
.comment-time { font-size: 12px; color: #94a3b8; }
.comment-content { color: #475569; line-height: 1.6; margin: 0; }
.child-comments { margin-top: 16px; padding: 16px; background: #f8fafc; border-radius: 8px; }
.child-comment { display: flex; gap: 12px; margin-bottom: 12px; }
.child-comment:last-child { margin-bottom: 0; }
.child-avatar { width: 32px; height: 32px; border-radius: 50%; }
.child-body { flex: 1; font-size: 14px; }
.child-username { font-weight: 500; color: #2563eb; margin-right: 8px; }
.child-text { color: #475569; }
.child-time { font-size: 12px; color: #94a3b8; margin-left: 12px; }
.reply-form { margin-top: 16px; display: flex; gap: 12px; }
.reply-input { flex: 1; }
.reply-input :deep(.el-input__inner) { border-radius: 8px; }
.no-comment { text-align: center; padding: 40px 0; color: #94a3b8; }
.no-comment i { font-size: 48px; margin-bottom: 12px; display: block; }
.no-comment p { font-size: 14px; margin: 0; }

/* 右侧章节目录 */
.chapter-sidebar { width: 340px; flex-shrink: 0; background: #fff; border-left: 1px solid #e2e8f0; height: 100vh; position: sticky; top: 0; overflow-y: auto; }
.chapter-sidebar::-webkit-scrollbar { width: 4px; }
.chapter-sidebar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 2px; }
.chapter-panel-header { padding: 20px; border-bottom: 1px solid #f1f5f9; display: flex; align-items: center; justify-content: space-between; }
.chapter-panel-header h3 { font-size: 16px; font-weight: 600; color: #1e293b; margin: 0; display: flex; align-items: center; gap: 8px; }
.chapter-panel-header h3 i { color: #2563eb; }
.chapter-total { font-size: 13px; color: #94a3b8; font-weight: 400; }
.chapter-list { padding: 8px 0; }
.chapter-group-title { display: flex; align-items: center; gap: 8px; padding: 12px 20px; font-size: 14px; font-weight: 600; color: #334155; cursor: pointer; transition: background 0.2s; }
.chapter-group-title:hover { background: #f8fafc; }
.chapter-group-title i { font-size: 12px; color: #94a3b8; }
.group-count { margin-left: auto; font-size: 12px; color: #94a3b8; font-weight: 400; }
.chapter-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 20px 10px 36px; cursor: pointer; transition: all 0.2s; border-left: 3px solid transparent; }
.chapter-item:hover { background: #f0f7ff; }
.chapter-item.active { background: #eff6ff; border-left-color: #2563eb; }
.chapter-item.active .chapter-item-title { color: #2563eb; font-weight: 500; }
.chapter-item-left { display: flex; align-items: center; gap: 8px; flex: 1; min-width: 0; }
.chapter-play-icon { color: #2563eb; font-size: 14px; flex-shrink: 0; }
.chapter-item-title { font-size: 13px; color: #475569; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chapter-item-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; margin-left: 8px; }
.chapter-duration { font-size: 12px; color: #94a3b8; }
.chapter-lock-icon { color: #d97706; font-size: 14px; }
.course-info-mini { padding: 16px 20px; border-top: 1px solid #f1f5f9; }
.info-row { display: flex; align-items: center; gap: 8px; padding: 8px 0; font-size: 13px; color: #64748b; }
.info-row i { color: #2563eb; font-size: 14px; }

@media (max-width: 1100px) {
  .video-learning-layout { flex-direction: column; }
  .chapter-sidebar { width: 100%; height: auto; position: static; border-left: none; border-top: 1px solid #e2e8f0; }
  .chapter-list { max-height: 400px; overflow-y: auto; }
}
@media (max-width: 600px) {
  .course-video { max-height: 240px; }
  .tab-item { padding: 12px 16px; font-size: 14px; }
}
</style>
