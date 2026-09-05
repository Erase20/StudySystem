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
        <el-table-column prop="type" label="课程类型">
          <template v-slot="scope">
            <span>{{ scope.row.type === 'VIDEO' ? '视频课' : scope.row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="所需积分"></el-table-column>
        <el-table-column prop="video" label="课程视频" show-overflow-tooltip>
          <template v-slot="scope">
            <el-button type="warning" size="small" icon="el-icon-download" @click="down(scope.row.video)" v-if="scope.row.video">下载</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="file" label="课程资料" show-overflow-tooltip></el-table-column>
        <el-table-column prop="recommend" label="是否推荐"></el-table-column>

        <el-table-column label="操作" width="180" align="center">
          <template v-slot="scope">
            <el-button type="primary" icon="el-icon-edit" @click="handleEdit(scope.row)" size="small">编辑</el-button>
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
        <el-form-item prop="recommend" label="是否推荐">
          <el-select v-model="form.recommend" placeholder="请选择" style="width: 100%">
            <el-option label="是" value="是"></el-option>
            <el-option label="否" value="否"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item prop="price" label="所需积分">
          <el-input v-model="form.price" autocomplete="off" placeholder="请输入"></el-input>
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


  </div>
</template>

<script>
import E from 'wangeditor'
export default {
  name: "Score",
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
      viewData: null
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
            url: this.form.id ? '/score/update' : '/score/add',
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
        this.$request.delete('/score/delete/' + id).then(res => {
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
        this.$request.delete('/score/delete/batch', {data: this.ids}).then(res => {
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
      this.$request.get('/score/selectPage', {
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
    }
  }
}
</script>

<style scoped>

</style>
