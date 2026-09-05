<template>
  <div class="register-container">
    <!-- 动态背景 -->
    <div class="bg-animation">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
      <div class="bg-shape shape-4"></div>
    </div>
    
    <!-- 注册卡片 -->
    <div class="register-card">
      <!-- Logo区域 -->
      <div class="register-header">
        <div class="logo-circle">
          <i class="el-icon-edit"></i>
        </div>
        <h1>创建账号</h1>
        <p>加入我们，开始学习之旅</p>
      </div>
      
      <!-- 表单区域 -->
      <el-form :model="form" :rules="rules" ref="formRef" class="register-form">
        <el-form-item prop="username">
          <el-input 
            prefix-icon="el-icon-user" 
            placeholder="请输入账号" 
            v-model="form.username"
            clearable
          ></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            prefix-icon="el-icon-lock" 
            placeholder="请输入密码" 
            show-password  
            v-model="form.password"
          ></el-input>
        </el-form-item>
        <el-form-item prop="confirmPass">
          <el-input 
            prefix-icon="el-icon-lock" 
            placeholder="请确认密码" 
            show-password  
            v-model="form.confirmPass"
            @keyup.enter.native="register"
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button class="register-btn" @click="register">
            <span>注 册</span>
            <i class="el-icon-right"></i>
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 底部链接 -->
      <div class="register-footer">
        <span>已有账号？</span>
        <a href="/login">立即登录</a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Register",
  data() {
    const validatePassword = (rule, confirmPass, callback) => {
      if (confirmPass === '') {
        callback(new Error('请确认密码'))
      } else if (confirmPass !== this.form.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    return {
      form: { role: 'USER'},
      rules: {
        username: [
          { required: true, message: '请输入账号', trigger: 'blur' },
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
        ],
        confirmPass: [
          { validator: validatePassword, trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    register() {
      this.$refs['formRef'].validate((valid) => {
        if (valid) {
          this.$request.post('/register', this.form).then(res => {
            if (res.code === '200') {
              this.$router.push('/login')
              this.$message.success('注册成功')
            } else {
              this.$message.error(res.msg)
            }
          })
        }
      })
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  position: relative;
  overflow: hidden;
}

/* 动态背景形状 */
.bg-animation {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;
}

.shape-1 {
  width: 400px;
  height: 400px;
  background: #fff;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 300px;
  height: 300px;
  background: #fff;
  bottom: -50px;
  left: -50px;
  animation-delay: 1s;
}

.shape-3 {
  width: 200px;
  height: 200px;
  background: #fff;
  top: 40%;
  right: 15%;
  animation-delay: 2s;
}

.shape-4 {
  width: 150px;
  height: 150px;
  background: #fff;
  bottom: 30%;
  left: 10%;
  animation-delay: 3s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-30px) rotate(10deg); }
}

/* 注册卡片 */
.register-card {
  width: 420px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 10;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Logo区域 */
.register-header {
  text-align: center;
  margin-bottom: 35px;
}

.logo-circle {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 10px 30px rgba(17, 153, 142, 0.4);
}

.logo-circle i {
  font-size: 36px;
  color: #fff;
}

.register-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.register-header p {
  font-size: 14px;
  color: #64748b;
}

/* 表单样式 */
.register-form {
  margin-top: 20px;
}

.register-form .el-input__inner {
  height: 48px;
  padding-left: 40px;
  font-size: 15px;
}

.register-form .el-input__prefix {
  left: 12px;
  font-size: 18px;
  color: #94a3b8;
}

/* 注册按钮 */
.register-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
  border: none !important;
  border-radius: 10px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease !important;
  box-shadow: 0 4px 15px rgba(17, 153, 142, 0.4) !important;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(17, 153, 142, 0.5) !important;
}

.register-btn:active {
  transform: translateY(0);
}

.register-btn i {
  transition: transform 0.3s ease;
}

.register-btn:hover i {
  transform: translateX(4px);
}

/* 底部链接 */
.register-footer {
  text-align: center;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
  font-size: 14px;
  color: #64748b;
}

.register-footer a {
  color: #11998e;
  font-weight: 500;
  margin-left: 5px;
  transition: color 0.3s;
}

.register-footer a:hover {
  color: #38ef7d;
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 480px) {
  .register-card {
    width: 90%;
    padding: 30px 25px;
  }
  
  .logo-circle {
    width: 60px;
    height: 60px;
  }
  
  .logo-circle i {
    font-size: 28px;
  }
  
  .register-header h1 {
    font-size: 24px;
  }
}
</style>
