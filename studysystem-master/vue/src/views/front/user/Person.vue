<template>
  <div class="person-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>个人中心</h2>
      <p>管理您的个人信息和账户设置</p>
    </div>

    <div class="person-content">
      <!-- 头像上传 -->
      <div class="avatar-section">
        <el-upload
          class="avatar-uploader"
          :action="$baseUrl + '/files/upload'"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
        >
          <img v-if="user.avatar" :src="$getImageUrl(user.avatar)" class="avatar" />
          <div v-else class="avatar-placeholder">
            <i class="el-icon-plus"></i>
          </div>
        </el-upload>
        <p class="avatar-tip">点击更换头像</p>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="updatePassword">修改密码</el-button>
      </div>

      <!-- 个人信息表单 -->
      <el-form :model="user" label-width="80px" class="person-form">
        <el-form-item label="用户名">
          <el-input v-model="user.username" disabled></el-input>
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="user.name" placeholder="请输入姓名"></el-input>
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="user.phone" placeholder="请输入电话"></el-input>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="user.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="积分">
          <el-input v-model="user.score" disabled></el-input>
        </el-form-item>
        <el-form-item label="学习方向">
          <el-checkbox-group v-model="selectedDirections" @change="onDirectionChange">
            <el-checkbox v-for="dir in directionOptions" :key="dir.key" :label="dir.key">{{ dir.name }}</el-checkbox>
          </el-checkbox-group>
          <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">选择感兴趣的方向，首页将优先推荐相关课程</div>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="update" class="save-btn">保存修改</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 修改密码弹窗 -->
    <el-dialog title="修改密码" :visible.sync="dialogVisible" width="400px">
      <el-form :model="user" label-width="80px" :rules="rules" ref="formRef">
        <el-form-item label="原始密码" prop="password">
          <el-input show-password v-model="user.password" placeholder="请输入原始密码"></el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input show-password v-model="user.newPassword" placeholder="请输入新密码"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input show-password v-model="user.confirmPassword" placeholder="请确认新密码"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">确定</el-button>
      </div>
    </el-dialog>

    <!-- 充值弹窗（保留功能但不主动展示） -->
    <el-dialog title="账户充值" :visible.sync="rechargeVisible" width="400px">
      <el-form label-width="80px">
        <el-form-item label="充值说明">
          <span style="color: #dc2626">一次性充值满500可成为会员</span>
        </el-form-item>
        <el-form-item label="充值金额">
          <el-input v-model="account" placeholder="请输入充值金额"></el-input>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-radio v-model="type" label="支付宝">支付宝</el-radio>
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="rechargeVisible = false">取消</el-button>
        <el-button type="primary" @click="pay">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 个人中心页面
 */
export default {
  data() {
    const validatePassword = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请确认密码'))
      } else if (value !== this.user.newPassword) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    return {
      user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
      selectedDirections: [],
      directionOptions: [
        { key: 'Java', name: 'Java开发' },
        { key: 'Python', name: 'Python' },
        { key: 'Vue', name: '前端开发' },
        { key: 'Web', name: 'Web开发' },
        { key: '数据库', name: '数据库' },
        { key: '架构', name: '架构设计' },
        { key: '算法', name: '算法' },
        { key: 'Linux', name: 'Linux' },
        { key: '爬虫', name: '爬虫' },
        { key: '测试', name: '软件测试' },
        { key: 'AI', name: '人工智能' },
      ],
      dialogVisible: false,
      rechargeVisible: false,
      account: null,
      type: '支付宝',
      rules: {
        password: [{ required: true, message: '请输入原始密码', trigger: 'blur' }],
        newPassword: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
        confirmPassword: [{ validator: validatePassword, required: true, trigger: 'blur' }]
      }
    }
  },
  
  created() {
    this.loadPerson()
  },
  
  methods: {
    onDirectionChange(val) {
      this.user.direction = val.join(',')
    },
    pay() {
      this.$request.get('/alipay/pay?price=' + this.account).then(res => {
        if (res.code === '200') {
          const div = document.createElement('div')
          div.innerHTML = res.data
          document.body.appendChild(div)
          document.forms[document.forms.length - 1].submit()
        }
      }).catch(() => {})
    },
    
    updatePassword() {
      this.dialogVisible = true
    },
    
    loadPerson() {
      this.$request.get('/user/selectById/' + this.user.id).then(res => {
        if (res.code === '200') {
          this.user = res.data
          localStorage.setItem('xm-user', JSON.stringify(this.user))
          // 初始化学习方向选择
          if (this.user.direction) {
            this.selectedDirections = this.user.direction.split(',')
          } else {
            this.selectedDirections = []
          }
        }
      }).catch(() => {})
    },
    
    update() {
      this.$request.put('/user/update', this.user).then(res => {
        if (res.code === '200') {
          this.$message.success('保存成功')
          localStorage.setItem('xm-user', JSON.stringify(this.user))
          this.$emit('update:user')
        } else {
          this.$message.error(res.msg)
        }
      }).catch(() => {})
    },
    
    handleAvatarSuccess(response) {
      this.$set(this.user, 'avatar', response.data)
    },
    
    save() {
      this.$refs.formRef.validate((valid) => {
        if (valid) {
          this.$request.put('/updatePassword', this.user).then(res => {
            if (res.code === '200') {
              this.$message.success('修改密码成功')
              this.$router.push('/login')
            } else {
              this.$message.error(res.msg)
            }
          }).catch(() => {})
        }
      })
    }
  }
}
</script>

<style scoped>
.person-page {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
  background: #fff;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
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

.person-content {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 32px;
}

.avatar-section {
  text-align: center;
  margin-bottom: 24px;
}

.avatar-uploader {
  display: inline-block;
}

.avatar-uploader :deep(.el-upload) {
  border: 2px dashed #e2e8f0;
  border-radius: 50%;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.3s;
}

.avatar-uploader :deep(.el-upload:hover) {
  border-color: #1e293b;
}

.avatar {
  width: 100px;
  height: 100px;
  display: block;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.avatar-placeholder i {
  font-size: 24px;
  color: #94a3b8;
}

.avatar-tip {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 12px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 32px;
}

.action-buttons .el-button--primary {
  background: #1e293b;
  border-color: #1e293b;
}

.action-buttons .el-button--primary:hover {
  background: #000;
  border-color: #000;
}

.person-form :deep(.el-input__inner) {
  background: #f8fafc;
}

.person-form :deep(.el-input.is-disabled .el-input__inner) {
  background: #f1f5f9;
  color: #64748b;
}

.save-btn {
  width: 100%;
  background: #1e293b;
  border-color: #1e293b;
}

.save-btn:hover {
  background: #000;
  border-color: #000;
}
</style>
