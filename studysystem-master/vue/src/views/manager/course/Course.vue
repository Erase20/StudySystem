<template>
  <div>
    <div class="search">
      <el-input placeholder="请输入课程名称" style="width: 200px" v-model="name"></el-input>
      <el-select v-model="recommend" placeholder="请选择是否推荐" style="width: 200px; margin-left: 5px">
        <el-option label="是" value="是"></el-option>
        <el-option label="否" value="否"></el-option>
      </el-select>
      <el-button type="primary" icon="el-icon-search" style="margin-left: 10px" @click="load(1)">查询</el-button>
      <el-button icon="el-icon-refresh" style="margin-left: 10px" @click="reset">重置</el-button>
    </div>

    <div class="operation">
      <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增</el-button>
      <el-button type="danger" icon="el-icon-delete" @click="delBatch">批量删除</el-button>
    </div>

    <div class="table">
      <el-table :data="tableData" stripe  @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" align="center"></el-table-column>
        <el-table-column prop="id" label="序号" width="80" align="center" sortable></el-table-column>
        <el-table-column prop="img" label="课程封面" show-overflow-tooltip>
          <template v-slot="scope">
            <div style="display: flex; align-items: center">
              <el-image style="width: 40px; height: 40px; border-radius: 10px" v-if="scope.row.img"
                        :src="getImageUrl(scope.row.img)" :preview-src-list="[getImageUrl(scope.row.img)]">
                <div slot="error" style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background: #f5f7fa;">
                  <i class="el-icon-picture-outline" style="font-size: 20px; color: #909399;"></i>
                </div>
              </el-image>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="课程名称" show-overflow-tooltip></el-table-column>
        <el-table-column prop="content" label="内容" show-overflow-tooltip>
          <template v-slot="scope" >
            <el-button type="success" size="small" icon="el-icon-view" @click="viewDataInit(scope.row.content)">查看</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="课程分类"></el-table-column>
        <el-table-column prop="price" label="课程价格"></el-table-column>
        <el-table-column prop="video" label="课程视频" show-overflow-tooltip>
          <template v-slot="scope">
            <el-button type="warning" size="small" icon="el-icon-download" @click="down(scope.row.video)" v-if="scope.row.video">下载</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="file" label="课程资料" show-overflow-tooltip></el-table-column>
        <el-table-column prop="discount" label="课程折扣"></el-table-column>
        <el-table-column prop="recommend" label="是否推荐"></el-table-column>

        <el-table-column label="操作" width="240" align="center">
          <template v-slot="scope">
            <el-button type="primary" icon="el-icon-edit" @click="handleEdit(scope.row)" size="small">编辑</el-button>
            <el-button type="success" icon="el-icon-notebook-2" @click="openChapterManager(scope.row)" size="small">章节</el-button>
            <el-button type="danger" icon="el-icon-delete" size="small" @click=del(scope.row.id)>删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
            background
            @current-change="handleCurrentChange"
            :current-page="pageNum"
            :page-sizes="[5, 10, 20]"
            :page-size="pageSize"
            layout="total, prev, pager, next"
            :total="total">
        </el-pagination>
      </div>
    </div>


    <el-dialog title="课程信息" :visible.sync="fromVisible" width="55%" :close-on-click-modal="false" destroy-on-close>
      <el-form label-width="100px" style="padding-right: 50px" :model="form" :rules="rules" ref="formRef">
        <el-form-item label="课程封面">
          <el-upload
              class="avatar-uploader"
              :action="$baseUrl + '/files/upload'"
              :headers="{ token: user.token }"
              list-type="picture"
              :on-success="handleImgSuccess"
          >
            <el-button type="primary">上传图片</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item prop="name" label="课程名称">
          <el-input v-model="form.name" autocomplete="off" placeholder="请输入课程名称"></el-input>
        </el-form-item>
        <el-form-item prop="type" label="课程类型">
          <el-select v-model="form.type" placeholder="请选择类型" style="width: 100%">
            <el-option label="视频课程" value="VIDEO"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="category" label="课程分类">
          <el-select v-model="form.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="Python开发" value="Python开发"></el-option>
            <el-option label="Java开发" value="Java开发"></el-option>
            <el-option label="人工智能" value="人工智能"></el-option>
            <el-option label="爬虫与自动化" value="爬虫与自动化"></el-option>
            <el-option label="前端开发" value="前端开发"></el-option>
            <el-option label="软件测试" value="软件测试"></el-option>
            <el-option label="数据库" value="数据库"></el-option>
            <el-option label="Linux运维" value="Linux运维"></el-option>
            <el-option label="数据结构" value="数据结构"></el-option>
            <el-option label="计算机基础" value="计算机基础"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="recommend" label="是否推荐">
          <el-select v-model="form.recommend" placeholder="请选择" style="width: 100%">
            <el-option label="是" value="是"></el-option>
            <el-option label="否" value="否"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="price" label="课程价格">
          <el-input v-model="form.price" autocomplete="off" placeholder="请输入价格"></el-input>
        </el-form-item>
        <el-form-item label="课程视频">
          <el-upload
              class="avatar-uploader"
              :action="$baseUrl + '/files/upload'"
              :headers="{ token: user.token }"
              :on-success="handleVideoSuccess"
          >
            <el-button type="primary">上传视频</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item prop="file" label="资料链接">
          <el-input v-model="form.file" autocomplete="off" placeholder="请输入资料链接"></el-input>
        </el-form-item>
        <el-form-item prop="discount" label="课程折扣">
          <el-input v-model="form.discount" autocomplete="off" placeholder="请输入课程折扣"></el-input>
        </el-form-item>
        <el-form-item prop="content" label="课程介绍">
          <div id="editor"></div>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="fromVisible = false">取 消</el-button>
        <el-button type="primary" @click="save">确 定</el-button>
      </div>
    </el-dialog>
    <el-dialog title="课程内容" :visible.sync="editorVisible" width="50%" :close-on-click-modal="false" destroy-on-close>
      <div v-html="viewData" class="w-e-text w-e-text-container"></div>
    </el-dialog>

    <!-- 章节管理弹窗 -->
    <el-dialog :title="'章节管理 - ' + (chapterCourse.name || '')" :visible.sync="chapterVisible" width="70%" :close-on-click-modal="false" destroy-on-close top="5vh">
      <div class="chapter-manager">
        <div class="chapter-toolbar">
          <el-button type="primary" size="small" icon="el-icon-plus" @click="addChapter">新增章节</el-button>
          <el-button type="warning" size="small" icon="el-icon-magic-stick" @click="autoGenerateChapters">自动生成目录</el-button>
          <span class="chapter-tip">共 {{ chapterList.length }} 个课时</span>
        </div>
        <el-table :data="chapterList" stripe border size="small" max-height="500">
          <el-table-column prop="sortOrder" label="序号" width="70" align="center"></el-table-column>
          <el-table-column prop="title" label="章节标题" min-width="200">
            <template v-slot="scope">
              <el-input v-if="scope.row._editing" v-model="scope.row.title" size="small" placeholder="章节标题"></el-input>
              <span v-else>{{ scope.row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="80" align="center">
            <template v-slot="scope">
              <el-select v-if="scope.row._editing" v-model="scope.row.type" size="small" style="width:70px">
                <el-option label="视频" value="VIDEO"></el-option>
              </el-select>
              <el-tag v-else type="primary" size="mini">视频</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="视频" width="200">
            <template v-slot="scope">
              <div v-if="scope.row._editing">
                <el-upload
                  :action="$baseUrl + '/files/upload'"
                  :headers="{ token: user.token }"
                  :on-success="(res) => scope.row.video = res.data"
                  :show-file-list="false"
                >
                  <el-button size="mini" type="primary">上传视频</el-button>
                </el-upload>
                <span v-if="scope.row.video" style="font-size:12px;color:#67c23a;margin-left:6px"><i class="el-icon-check"></i> 已上传</span>
              </div>
              <span v-else-if="scope.row.video" style="color:#67c23a;font-size:12px"><i class="el-icon-video-camera-solid"></i> 有视频</span>
              <span v-else style="color:#909399;font-size:12px">无</span>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="时长(秒)" width="100" align="center">
            <template v-slot="scope">
              <el-input-number v-if="scope.row._editing" v-model="scope.row.duration" size="small" :min="0" :max="99999" controls-position="right" style="width:90px"></el-input-number>
              <span v-else>{{ scope.row.duration ? formatDuration(scope.row.duration) : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="freePreview" label="免费试看" width="90" align="center">
            <template v-slot="scope">
              <el-switch v-if="scope.row._editing" v-model="scope.row.freePreview" :active-value="1" :inactive-value="0" size="small"></el-switch>
              <el-tag v-else :type="scope.row.freePreview ? 'success' : 'info'" size="mini">{{ scope.row.freePreview ? '是' : '否' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" align="center">
            <template v-slot="scope">
              <template v-if="scope.row._editing">
                <el-button type="success" size="mini" @click="saveChapter(scope.row)">保存</el-button>
                <el-button size="mini" @click="cancelEditChapter(scope.row)">取消</el-button>
              </template>
              <template v-else>
                <el-button type="primary" size="mini" @click="editChapter(scope.row)">编辑</el-button>
                <el-button type="danger" size="mini" @click="delChapter(scope.row)">删除</el-button>
              </template>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>


  </div>
</template>

<script>
import E from 'wangeditor'
export default {
  name: "Course",
  data() {
    return {
      editor: null,
      tableData: [],  // 所有的数据
      pageNum: 1,   // 当前的页码
      pageSize: 10,  // 每页显示的个数
      total: 0,
      name: null,
      recommend: null,
      fromVisible: false,
      editorVisible: false,
      form: {},
      user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
      rules: {
        name: [
          {required: true, message: '请输入课程名称', trigger: 'blur'},
        ],
        type: [
          {required: true, message: '请选择课程类型', trigger: 'blur'},
        ],
        recommend: [
          {required: true, message: '是否推荐', trigger: 'blur'},
        ],
        price: [
          {required: true, message: '请输入课程价格', trigger: 'blur'},
        ]
      },
      ids: [],
      viewData: null,
      // 章节管理
      chapterVisible: false,
      chapterCourse: {},
      chapterList: []
    }
  },
  created() {
    this.load(1)
  },
  methods: {
    initWangEditor(content) {
      this.$nextTick(() => {
        this.editor = new E('#editor')
        this.editor.config.placeholder = '请输入内容'
        this.editor.config.uploadFileName = 'file'
        this.editor.config.uploadImgServer = 'http://localhost:9090/files/wang/upload'
        this.editor.create()
        setTimeout(() => {
          this.editor.txt.html(content)
        })
      })
    },
    viewDataInit(data){
      this.viewData = data
      this.editorVisible = true
    },
    handleAdd() {   // 新增数据
      this.form = {}  // 新增数据的时候清空数据
      this.fromVisible = true   // 打开弹窗
      this.initWangEditor('')   //初始化富文本
    },
    handleEdit(row) {   // 编辑数据
      this.form = JSON.parse(JSON.stringify(row))  // 给form对象赋值  注意要深拷贝数据
      this.fromVisible = true   // 打开弹窗
      this.initWangEditor(this.form.content || '')
    },
    save() {   // 保存按钮触发的逻辑  它会触发新增或者更新
      this.$refs.formRef.validate((valid) => {
        if (valid) {
          this.form.content = this.editor.txt.html()
          this.$request({
            url: this.form.id ? '/course/update' : '/course/add',
            method: this.form.id ? 'PUT' : 'POST',
            data: this.form
          }).then(res => {
            if (res.code === '200') {  // 表示成功保存
              this.$message.success('保存成功')
              this.load(1)
              this.fromVisible = false
            } else {
              this.$message.error(res.msg)  // 弹出错误的信息
            }
          })
        }
      })
    },
    del(id) {   // 单个删除
      this.$confirm('您确定删除吗？', '确认删除', {type: "warning"}).then(response => {
        this.$request.delete('/course/delete/' + id).then(res => {
          if (res.code === '200') {   // 表示操作成功
            this.$message.success('操作成功')
            this.load(1)
          } else {
            this.$message.error(res.msg)  // 弹出错误的信息
          }
        })
      }).catch(() => {
      })
    },
    handleSelectionChange(rows) {   // 当前选中的所有的行数据
      this.ids = rows.map(v => v.id)   //  [1,2]
    },
    delBatch() {   // 批量删除
      if (!this.ids.length) {
        this.$message.warning('请选择数据')
        return
      }
      this.$confirm('您确定批量删除这些数据吗？', '确认删除', {type: "warning"}).then(response => {
        this.$request.delete('/course/delete/batch', {data: this.ids}).then(res => {
          if (res.code === '200') {   // 表示操作成功
            this.$message.success('操作成功')
            this.load(1)
          } else {
            this.$message.error(res.msg)  // 弹出错误的信息
          }
        })
      }).catch(() => {
      })
    },
    load(pageNum) {  // 分页查询
      if (pageNum) this.pageNum = pageNum
      this.$request.get('/course/selectPage', {
        params: {
          pageNum: this.pageNum,
          pageSize: this.pageSize,
          name: this.name,
          recommend: this.recommend,
        }
      }).then(res => {
        this.tableData = res.data?.list
        this.total = res.data?.total
      })
    },
    reset() {
      this.name = null
      this.recommend = null
      this.load(1)
    },
    handleCurrentChange(pageNum) {
      this.load(pageNum)
    },
    handleImgSuccess(res){
      this.form.img = res.data
    },
    handleVideoSuccess(res){
      this.form.video = res.data
    },
    down(url){
      window.open(url, '_blank')
    },
    // 处理图片URL，确保返回完整的URL路径
    getImageUrl(img) {
      if (!img) return ''
      return this.$getImageUrl(img)
    },
    // ========== 章节管理 ==========
    openChapterManager(row) {
      this.chapterCourse = row
      this.chapterVisible = true
      this.loadChapters()
    },
    loadChapters() {
      this.$request.get('/chapter/course/' + this.chapterCourse.id).then(res => {
        if (res.code === '200') {
          this.chapterList = (res.data || []).map(ch => Object.assign({}, ch, { _editing: false }))
        }
      })
    },
    addChapter() {
      const maxSort = this.chapterList.length ? Math.max(...this.chapterList.map(c => c.sortOrder || 0)) : 0
      this.chapterList.push({
        id: null,
        courseId: this.chapterCourse.id,
        title: '',
        sortOrder: maxSort + 1,
        type: 'VIDEO',
        video: null,
        duration: 0,
        freePreview: 0,
        _editing: true,
        _isNew: true
      })
    },
    editChapter(row) {
      this.$set(row, '_editing', true)
      this.$set(row, '_backup', JSON.parse(JSON.stringify(row)))
    },
    cancelEditChapter(row) {
      if (row._isNew) {
        this.chapterList = this.chapterList.filter(c => c !== row)
      } else {
        Object.assign(row, row._backup, { _editing: false })
      }
    },
    saveChapter(row) {
      if (!row.title) {
        this.$message.warning('请输入章节标题')
        return
      }
      const data = {
        id: row.id,
        courseId: this.chapterCourse.id,
        title: row.title,
        sortOrder: row.sortOrder,
        type: row.type,
        video: row.video,
        duration: row.duration,
        freePreview: row.freePreview
      }
      const url = data.id ? '/chapter/update' : '/chapter/add'
      const method = data.id ? 'PUT' : 'POST'
      this.$request({ url, method, data }).then(res => {
        if (res.code === '200') {
          this.$message.success('保存成功')
          this.loadChapters()
        } else {
          this.$message.error(res.msg)
        }
      })
    },
    delChapter(row) {
      if (!row.id) {
        this.chapterList = this.chapterList.filter(c => c !== row)
        return
      }
      this.$confirm('确定删除该章节？', '确认', { type: 'warning' }).then(() => {
        this.$request.delete('/chapter/delete/' + row.id).then(res => {
          if (res.code === '200') {
            this.$message.success('删除成功')
            this.loadChapters()
          } else {
            this.$message.error(res.msg)
          }
        })
      }).catch(() => {})
    },
    autoGenerateChapters() {
      this.$confirm('自动生成将先清空当前课程所有章节，是否继续？', '确认', { type: 'warning' }).then(() => {
        // 先删除现有章节
        const delPromises = this.chapterList.filter(c => c.id).map(c => this.$request.delete('/chapter/delete/' + c.id))
        Promise.all(delPromises).then(() => {
          // 根据课程名生成章节
          this.generateForCourse()
        })
      }).catch(() => {})
    },
    generateForCourse() {
      const name = (this.chapterCourse.name || '').toLowerCase()
      const templates = this.getChapterTemplate(name)
      let sortOrder = 1
      const addPromises = templates.map(t => {
        const data = { courseId: this.chapterCourse.id, title: t[0], sortOrder: sortOrder++, type: 'VIDEO', duration: parseInt(t[1]), freePreview: sortOrder <= 3 ? 1 : 0 }
        return this.$request.post('/chapter/add', data)
      })
      Promise.all(addPromises).then(() => {
        this.$message.success('已生成 ' + templates.length + ' 个章节')
        this.loadChapters()
      }).catch(() => {
        this.$message.error('生成失败')
      })
    },
    getChapterTemplate(name) {
      if (name.includes('python')) return [['1-1 Python开发环境搭建','900'],['1-2 基础语法入门','1200'],['1-3 变量与数据类型','1500'],['1-4 条件语句与循环','1200'],['1-5 函数与模块','1600'],['2-1 面向对象编程','2000'],['2-2 文件操作与异常处理','1400'],['2-3 综合实战项目','2400']]
      if (name.includes('java')) return [['1-1 Java开发环境配置','800'],['1-2 基础语法','1200'],['1-3 面向对象基础','1800'],['1-4 面向对象进阶','2000'],['1-5 异常处理与常用类','1400'],['2-1 集合框架','2200'],['2-2 IO流与文件操作','1600'],['2-3 多线程编程','2000'],['2-4 网络编程基础','1800']]
      if (name.includes('vue')) return [['1-1 Vue简介与环境搭建','600'],['1-2 模板语法与数据绑定','1200'],['1-3 计算属性与侦听器','1000'],['1-4 条件渲染与列表渲染','1200'],['1-5 事件处理与表单绑定','1400'],['2-1 组件基础','1600'],['2-2 组件通信','1800'],['2-3 Vue Router路由','1500'],['2-4 Vuex状态管理','1800']]
      if (name.includes('前端') || name.includes('html') || name.includes('javascript') || name.includes('web')) return [['1-1 HTML基础','900'],['1-2 CSS样式入门','1200'],['1-3 CSS布局与动画','1500'],['1-4 JavaScript基础','1800'],['1-5 DOM操作与事件','1400'],['2-1 ES6+新特性','1600'],['2-2 异步编程','1200'],['2-3 前端工程化','1500']]
      if (name.includes('数据库') || name.includes('mysql')) return [['1-1 数据库基础概念','800'],['1-2 MySQL安装与配置','600'],['1-3 SQL基础查询','1500'],['1-4 多表连接查询','1800'],['1-5 索引与性能优化','2000'],['2-1 存储过程与函数','1600'],['2-2 事务与锁机制','1400'],['2-3 数据库设计实战','2200']]
      if (name.includes('linux')) return [['1-1 Linux系统安装','800'],['1-2 文件系统与目录操作','1200'],['1-3 用户与权限管理','1000'],['1-4 进程与服务管理','1400'],['2-1 Shell脚本编程','2000'],['2-2 网络配置与防火墙','1200'],['2-3 服务器部署实战','1800']]
      if (name.includes('爬虫')) return [['1-1 爬虫原理与法律须知','600'],['1-2 HTTP请求与响应','1000'],['1-3 HTML解析与数据提取','1500'],['1-4 数据存储','1200'],['2-1 动态网页爬取','1800'],['2-2 反爬虫策略与应对','1600'],['2-3 分布式爬虫实战','2200']]
      if (name.includes('深度学习') || name.includes('pytorch') || name.includes('机器学习') || name.includes('ai')) return [['1-1 概述与环境搭建','800'],['1-2 数学基础回顾','1200'],['1-3 机器学习基础','1500'],['1-4 特征工程','1400'],['2-1 监督学习算法','2000'],['2-2 无监督学习算法','1600'],['2-3 深度学习入门','2200'],['2-4 模型评估与调优','1800']]
      if (name.includes('测试')) return [['1-1 软件测试基础','800'],['1-2 测试用例设计','1200'],['1-3 功能测试实战','1500'],['1-4 接口测试','1400'],['2-1 UI自动化测试','1800'],['2-2 性能测试入门','1600'],['2-3 持续集成与DevOps','1200']]
      if (name.includes('架构') || name.includes('spring')) return [['1-1 架构设计原则','900'],['1-2 单体与微服务','1200'],['1-3 分布式系统基础','1500'],['1-4 高可用设计','1800'],['2-1 消息队列','1600'],['2-2 缓存架构','1400'],['2-3 数据库分库分表','2000']]
      // 默认
      return [['1-1 课程导学','500'],['1-2 基础入门','1200'],['1-3 核心概念','1500'],['1-4 进阶内容','1800'],['2-1 实战演练','2000'],['2-2 综合应用','1600'],['2-3 课程总结','800']]
    },
    formatDuration(seconds) {
      if (!seconds) return '-'
      const m = Math.floor(seconds / 60)
      const s = seconds % 60
      return m + ':' + (s < 10 ? '0' : '') + s
    }
  }
}
</script>

<style scoped>
.chapter-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.chapter-tip {
  margin-left: auto;
  color: #909399;
  font-size: 13px;
}
</style>
