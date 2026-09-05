<template>
  <div class="info-detail-page">
    <!-- 面包屑 -->
    <div class="breadcrumb-bar">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/front/home' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/front/information' }">学习资源</el-breadcrumb-item>
        <el-breadcrumb-item>{{ informationData.name || '资源详情' }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="detail-container">
      <!-- 左侧：封面 + 文件信息 -->
      <div class="left-panel">
        <div class="cover-card">
          <img v-if="informationData.img" :src="getImageUrl(informationData.img)" class="cover-img" @error="handleImgError">
          <div v-else class="cover-placeholder">
            <i :class="fileTypeIcon" style="font-size: 64px; color: #94a3b8;"></i>
          </div>
          <div class="file-type-badge" :class="fileTypeClass">
            <i :class="fileTypeIcon"></i>
            {{ fileTypeLabel }}
          </div>
        </div>

        <div class="file-info-card">
          <div class="info-row">
            <span class="info-label"><i class="el-icon-user"></i> 上传者</span>
            <span class="info-value">{{ informationData.userName || '未知用户' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label"><i class="el-icon-time"></i> 发布时间</span>
            <span class="info-value">{{ informationData.time }}</span>
          </div>
          <div class="info-row">
            <span class="info-label"><i class="el-icon-download"></i> 下载次数</span>
            <span class="info-value">{{ downloadCount }} 次</span>
          </div>
          <div class="info-row">
            <span class="info-label"><i class="el-icon-coin"></i> 所需积分</span>
            <span class="info-value" :class="informationData.score > 0 ? 'need-score' : 'free-text'">
              {{ informationData.score > 0 ? informationData.score + ' 积分' : '免费' }}
            </span>
          </div>
          <div class="info-row" v-if="informationData.status">
            <span class="info-label"><i class="el-icon-check"></i> 审核状态</span>
            <el-tag size="mini" :type="statusTagType">{{ informationData.status }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 右侧：资料内容 -->
      <div class="right-panel">
        <div class="header-section">
          <h1 class="info-title">{{ informationData.name }}</h1>
          <div class="meta-tags">
            <span class="meta-tag type-tag"><i :class="fileTypeIcon"></i> {{ fileTypeLabel }}</span>
            <span class="meta-tag score-tag" v-if="informationData.score > 0"><i class="el-icon-coin"></i> {{ informationData.score }} 积分</span>
            <span class="meta-tag free-tag" v-else><i class="el-icon-present"></i> 免费</span>
            <span class="meta-tag" v-if="informationData.recommend === '是'"><i class="el-icon-star-on"></i> 推荐</span>
          </div>
        </div>

        <!-- 下载/兑换区域 -->
        <div class="action-card">
          <div v-if="informationData.score === 0 || flag || isOwner">
            <div v-if="isOwner" class="owner-badge">
              <el-tag type="success" size="small"><i class="el-icon-user"></i> 我上传的资料</el-tag>
            </div>
            <el-button type="primary" size="medium" class="download-btn" @click="downloadFile">
              <i class="el-icon-download"></i> 立即下载
            </el-button>
            <span class="action-tip">文件链接：<a :href="resolveFileUrl(informationData.file)" target="_blank">{{ fileName }}</a></span>
          </div>
          <div v-else class="exchange-area">
            <div class="exchange-info">
              <i class="el-icon-lock" style="font-size: 24px; color: #f59e0b;"></i>
              <span class="exchange-text">该资料需要 <strong>{{ informationData.score }}</strong> 积分兑换后可下载</span>
            </div>
            <el-button type="warning" size="medium" class="exchange-btn" @click="exchange">
              <i class="el-icon-coin"></i> 兑换资料
            </el-button>
          </div>
        </div>

        <!-- 资料介绍 -->
        <div class="content-section">
          <div class="section-title">
            <i class="el-icon-document"></i> 资料介绍
          </div>
          <div class="content-body" v-html="informationData.content || '<p style=\'color:#94a3b8\'>暂无资料介绍</p>'"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
      informationId: this.$route.query.id,
      informationData: {},
      flag: false,
      downloadCount: 0
    }
  },
  computed: {
    fileType() {
      const file = this.informationData.file || ''
      const ext = file.split('.').pop()?.toLowerCase() || ''
      const typeMap = {
        pdf: 'pdf',
        doc: 'doc', docx: 'doc',
        ppt: 'ppt', pptx: 'ppt',
        xls: 'xls', xlsx: 'xls',
        zip: 'zip', rar: 'zip', '7z': 'zip',
        java: 'code', py: 'code', js: 'code', vue: 'code', html: 'code', css: 'code', cpp: 'code', c: 'code', go: 'code',
        md: 'note', txt: 'note',
        jpg: 'image', jpeg: 'image', png: 'image', gif: 'image', webp: 'image',
        mp4: 'video', avi: 'video', mkv: 'video'
      }
      return typeMap[ext] || 'other'
    },
    fileTypeLabel() {
      const labels = {
        pdf: 'PDF文档', doc: 'Word文档', ppt: 'PPT文档', xls: 'Excel表格',
        zip: '压缩包', code: '源码文件', note: '文本笔记',
        image: '图片文件', video: '视频文件', other: '其他文件'
      }
      return labels[this.fileType] || '其他文件'
    },
    fileTypeIcon() {
      const icons = {
        pdf: 'el-icon-document',
        doc: 'el-icon-document',
        ppt: 'el-icon-data-board',
        xls: 'el-icon-data-analysis',
        zip: 'el-icon-box',
        code: 'el-icon-cpu',
        note: 'el-icon-notebook-2',
        image: 'el-icon-picture',
        video: 'el-icon-video-camera',
        other: 'el-icon-document'
      }
      return icons[this.fileType] || 'el-icon-document'
    },
    fileTypeClass() {
      return 'type-' + this.fileType
    },
    statusTagType() {
      const map = { '审核通过': 'success', '待审核': 'warning', '审核不通过': 'danger' }
      return map[this.informationData.status] || 'info'
    },
    isOwner() {
      return this.user.id && this.informationData.userId === this.user.id
    },
    fileName() {
      const file = this.informationData.file || ''
      return file.split('/').pop() || file
    }
  },
  mounted() {
    this.loadInformation()
    this.check()
    this.loadDownloadCount()
  },
  methods: {
    check() {
      if (!this.user.id) return
      this.$request.get('/fileorder/selectAll', {
        params: { userId: this.user.id, fileId: this.informationId }
      }).then(res => {
        if (res.code === '200' && res.data?.length > 0) {
          this.flag = true
        }
      })
    },
    loadDownloadCount() {
      this.$request.get('/fileorder/selectAll', {
        params: { fileId: this.informationId }
      }).then(res => {
        if (res.code === '200') {
          this.downloadCount = res.data?.length || 0
        }
      })
    },
    exchange() {
      if (!this.user.id) {
        this.$message.warning('请先登录')
        return
      }
      this.$request.post('/fileorder/add', {
        fileId: this.informationId,
        userId: this.user.id,
        score: this.informationData.score
      }).then(res => {
        if (res.code === '200') {
          this.$message.success('兑换成功')
          this.flag = true
          this.loadDownloadCount()
        } else {
          this.$message.error(res.msg)
        }
      })
    },
    downloadFile() {
      const fileUrl = this.getDownloadUrl(this.informationData.file)
      if (fileUrl) {
        window.open(fileUrl, '_blank')
        this.loadDownloadCount()
      } else {
        this.$message.warning('文件链接不存在')
      }
    },
    resolveFileUrl(file) {
      if (!file) return ''
      if (file.startsWith('http')) return file
      return this.$baseUrl + file
    },
    getDownloadUrl(file) {
      if (!file) return ''
      // 将文件URL转为下载接口URL
      let baseUrl = this.resolveFileUrl(file)
      // http://localhost:9090/files/xxx.jpg → http://localhost:9090/files/download/xxx.jpg
      return baseUrl.replace('/files/', '/files/download/')
    },
    loadInformation() {
      this.$request.get('/information/selectById/' + this.informationId).then(res => {
        if (res.code === '200') {
          this.informationData = res.data
        } else {
          this.$message.error(res.msg)
        }
      })
    },
    getImageUrl(img) {
      if (!img) return ''
      return this.$getImageUrl(img)
    },
    handleImgError(e) {
      e.target.style.display = 'none'
      e.target.nextElementSibling.style.display = 'flex'
    }
  }
}
</script>

<style scoped>
.info-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  min-height: 100vh;
}

.breadcrumb-bar {
  margin-bottom: 20px;
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
}

.detail-container {
  display: flex;
  gap: 24px;
}

/* 左侧面板 */
.left-panel {
  width: 320px;
  flex-shrink: 0;
}

.cover-card {
  position: relative;
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
  border: 1px solid #e2e8f0;
}

.cover-img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.cover-placeholder {
  width: 100%;
  height: 200px;
  display: none;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
}

.file-type-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 4px;
}

.type-pdf { background: #dc2626; }
.type-doc { background: #2563eb; }
.type-ppt { background: #ea580c; }
.type-xls { background: #16a34a; }
.type-zip { background: #7c3aed; }
.type-code { background: #0ea5e9; }
.type-note { background: #64748b; }
.type-image { background: #db2777; }
.type-video { background: #ca8a04; }
.type-other { background: #475569; }

.file-info-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f1f5f9;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: #64748b;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-value {
  color: #1e293b;
  font-size: 14px;
  font-weight: 500;
}

.need-score { color: #dc2626; }
.free-text { color: #16a34a; }

/* 右侧面板 */
.right-panel {
  flex: 1;
  min-width: 0;
}

.header-section {
  margin-bottom: 20px;
}

.info-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.meta-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
  background: #f1f5f9;
  color: #475569;
}

.type-tag {
  background: #e0f2fe;
  color: #0369a1;
}

.score-tag {
  background: #fef3c7;
  color: #92400e;
}

.free-tag {
  background: #dcfce7;
  color: #166534;
}

/* 操作卡片 */
.action-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
}

.owner-badge {
  margin-bottom: 12px;
}

.download-btn {
  background: #1e293b;
  border-color: #1e293b;
  padding: 12px 32px;
  font-size: 16px;
}

.download-btn:hover {
  background: #000;
  border-color: #000;
}

.action-tip {
  display: block;
  margin-top: 12px;
  color: #64748b;
  font-size: 13px;
  word-break: break-all;
}

.action-tip a {
  color: #2563eb;
}

.exchange-area {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.exchange-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.exchange-text {
  color: #475569;
  font-size: 15px;
}

.exchange-btn {
  background: #f59e0b;
  border-color: #f59e0b;
  padding: 12px 32px;
  font-size: 16px;
}

.exchange-btn:hover {
  background: #d97706;
  border-color: #d97706;
}

/* 内容区域 */
.content-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-body {
  line-height: 1.8;
  color: #334155;
}

.content-body >>> img {
  max-width: 100%;
  border-radius: 8px;
}

.content-body >>> p {
  margin: 8px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .detail-container {
    flex-direction: column;
  }
  .left-panel {
    width: 100%;
  }
  .info-title {
    font-size: 20px;
  }
}
</style>
