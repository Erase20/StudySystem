<template>
  <div class="information-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>学习资源</h2>
      <p>海量学习资料，助力知识积累</p>
    </div>

    <!-- 搜索区域 -->
    <div class="search-section">
      <el-input 
        placeholder="请输入资源名称" 
        v-model="name"
        prefix-icon="el-icon-search"
        @keyup.enter.native="load(1)"
      ></el-input>
      <el-button type="primary" @click="load(1)">查询</el-button>
      <el-button @click="reset">重置</el-button>
      <el-button type="success" icon="el-icon-upload2" @click="goUpload" v-if="user.id">上传资料</el-button>
    </div>

    <!-- 资源表格 -->
    <div class="info-table">
      <el-table :data="tableData" stripe>
        <el-table-column prop="id" label="序号" width="70" align="center"></el-table-column>
        <el-table-column label="类型" width="80" align="center">
          <template v-slot="scope">
            <div class="file-type-icon" :class="'type-' + getFileType(scope.row.file)">
              <i :class="getFileTypeIcon(scope.row.file)"></i>
              <span class="type-label">{{ getFileTypeLabel(scope.row.file) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="img" label="封面" width="90">
          <template v-slot="scope">
            <div class="cover-wrapper">
              <el-image 
                style="width: 60px; height: 40px; border-radius: 4px;" 
                v-if="scope.row.img"
                :src="getImageUrl(scope.row.img)" 
                :preview-src-list="[getImageUrl(scope.row.img)]"
              >
                <div slot="error" class="image-error">
                  <i :class="getFileTypeIcon(scope.row.file)"></i>
                </div>
              </el-image>
              <div v-else class="image-error">
                <i :class="getFileTypeIcon(scope.row.file)"></i>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="资源名称" min-width="250">
          <template v-slot="scope">
            <a class="info-link" :href="'/front/informationDetail?id=' + scope.row.id">{{ scope.row.name }}</a>
            <el-tag size="mini" type="warning" v-if="scope.row.recommend === '是'" style="margin-left: 6px;">推荐</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="userName" label="上传用户" width="110"></el-table-column>
        <el-table-column prop="score" label="所需积分" width="100" align="center">
          <template v-slot="scope">
            <span class="price" v-if="scope.row.score > 0">{{ scope.row.score }}</span>
            <span class="free" v-else>免费</span>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="发布时间" width="110"></el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template v-slot="scope">
            <!-- 自己上传的 — 直接下载 -->
            <el-button 
              type="success" 
              size="mini"
              icon="el-icon-download"
              v-if="scope.row.userId === user.id"
              @click="downloadRow(scope.row)"
            >下载</el-button>
            <!-- 免费 或 已兑换 — 下载 -->
            <el-button 
              type="success" 
              size="mini"
              icon="el-icon-download"
              v-else-if="scope.row.score === 0 || isDownloaded(scope.row.id)"
              @click="goDetail(scope.row.id)"
            >下载</el-button>
            <!-- 需积分未兑换 — 兑换 -->
            <el-button 
              type="warning" 
              size="mini"
              icon="el-icon-coin"
              v-else
              @click="exchange(scope.row)"
            >{{ scope.row.score }}积分</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
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
  </div>
</template>

<script>
/**
 * 学习资源列表页面
 */
export default {
  data() {
    return {
      tableData: [],
      pageNum: 1,
      pageSize: 10,
      total: 0,
      name: null,
      user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
      myFileOrders: []
    }
  },

  mounted() {
    this.load(1)
    this.loadMyFileOrders()
  },

  methods: {
    load(pageNum) {
      if (pageNum) this.pageNum = pageNum
      this.$request.get('/information/selectPage', {
        params: {
          pageNum: this.pageNum,
          pageSize: this.pageSize,
          name: this.name,
          status: '审核通过'
        }
      }).then(res => {
        this.tableData = res.data?.list || []
        this.total = res.data?.total || 0
      }).catch(() => {})
    },

    loadMyFileOrders() {
      if (!this.user.id) return
      this.$request.get('/fileorder/selectAll', {
        params: { userId: this.user.id }
      }).then(res => {
        if (res.code === '200') {
          this.myFileOrders = res.data || []
        }
      }).catch(() => {})
    },

    isDownloaded(fileId) {
      return this.myFileOrders.some(item => item.fileId === fileId)
    },

    exchange(row) {
      if (!this.user.id) {
        this.$message.warning('请先登录')
        return
      }
      this.$request.post('/fileorder/add', {
        fileId: row.id,
        userId: this.user.id,
        score: row.score
      }).then(res => {
        if (res.code === '200') {
          this.$message.success('兑换成功')
          this.loadMyFileOrders()
        } else {
          this.$message.error(res.msg)
        }
      })
    },

    goDetail(id) {
      this.$router.push('/front/informationDetail?id=' + id)
    },

    downloadRow(row) {
      const fileUrl = this.getDownloadUrl(row.file)
      if (fileUrl) {
        window.open(fileUrl, '_blank')
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
      let baseUrl = this.resolveFileUrl(file)
      return baseUrl.replace('/files/', '/files/download/')
    },

    goUpload() {
      this.$router.push('/front/myInfo')
    },

    getFileType(file) {
      const ext = (file || '').split('.').pop()?.toLowerCase() || ''
      const map = {
        pdf: 'pdf', doc: 'doc', docx: 'doc', ppt: 'ppt', pptx: 'ppt',
        xls: 'xls', xlsx: 'xls', zip: 'zip', rar: 'zip', '7z': 'zip',
        java: 'code', py: 'code', js: 'code', vue: 'code', html: 'code', css: 'code', cpp: 'code', c: 'code', go: 'code',
        md: 'note', txt: 'note',
        jpg: 'image', jpeg: 'image', png: 'image', gif: 'image',
        mp4: 'video', avi: 'video', mkv: 'video'
      }
      return map[ext] || 'other'
    },

    getFileTypeIcon(file) {
      const type = this.getFileType(file)
      const icons = {
        pdf: 'el-icon-document', doc: 'el-icon-document', ppt: 'el-icon-data-board',
        xls: 'el-icon-data-analysis', zip: 'el-icon-box', code: 'el-icon-cpu',
        note: 'el-icon-notebook-2', image: 'el-icon-picture',
        video: 'el-icon-video-camera', other: 'el-icon-document'
      }
      return icons[type] || 'el-icon-document'
    },

    getFileTypeLabel(file) {
      const type = this.getFileType(file)
      const labels = {
        pdf: 'PDF', doc: '文档', ppt: 'PPT', xls: '表格',
        zip: '压缩包', code: '源码', note: '笔记',
        image: '图片', video: '视频', other: '文件'
      }
      return labels[type] || '文件'
    },

    reset() {
      this.name = null
      this.load(1)
    },

    handleCurrentChange(pageNum) {
      this.load(pageNum)
    },

    getImageUrl(img) {
      if (!img) return ''
      return this.$getImageUrl(img)
    }
  }
}
</script>

<style scoped>
.information-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

.page-header {
  margin-bottom: 24px;
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

.search-section {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.search-section .el-input {
  width: 300px;
}

.search-section .el-button--primary {
  background: #1e293b;
  border-color: #1e293b;
}

.search-section .el-button--primary:hover {
  background: #000;
  border-color: #000;
}

.info-table {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.cover-wrapper {
  display: flex;
  align-items: center;
}

.image-error {
  width: 60px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  border-radius: 4px;
}

.image-error i {
  font-size: 20px;
  color: #94a3b8;
}

.file-type-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.file-type-icon i {
  font-size: 20px;
}

.file-type-icon .type-label {
  font-size: 11px;
  font-weight: 500;
}

.type-pdf i { color: #dc2626; }
.type-doc i { color: #2563eb; }
.type-ppt i { color: #ea580c; }
.type-xls i { color: #16a34a; }
.type-zip i { color: #7c3aed; }
.type-code i { color: #0ea5e9; }
.type-note i { color: #64748b; }
.type-image i { color: #db2777; }
.type-video i { color: #ca8a04; }
.type-other i { color: #475569; }

.info-link {
  color: #1e293b;
  text-decoration: none;
  font-weight: 500;
}

.info-link:hover {
  color: #000;
}

.price {
  color: #dc2626;
  font-weight: 600;
}

.free {
  color: #1e293b;
  font-weight: 500;
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled).active) {
  background: #1e293b;
}

:deep(.el-pagination.is-background .el-pager li:not(.disabled):hover) {
  color: #1e293b;
}

/* 响应式 */
@media (max-width: 768px) {
  .information-page {
    padding: 16px;
  }

  .page-header h2 {
    font-size: 20px;
  }

  .search-section {
    flex-direction: column;
  }

  .search-section .el-input {
    width: 100%;
  }

  .info-table {
    padding: 12px;
    overflow-x: auto;
  }

  .pagination {
    justify-content: center;
  }
}
</style>
