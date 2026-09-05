<template>
  <!-- 登录页面根容器 - 知识星河主题 -->
  <div class="login-container">
    <!-- 星河背景 -->
    <div class="starfield">
      <!-- 星星层 -->
      <div class="stars">
        <div v-for="i in 50" :key="i" class="star" :style="getStarStyle(i)"></div>
      </div>
      <!-- 星座连线 -->
      <svg class="constellation" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
        <line v-for="(line, idx) in constellationLines" :key="idx"
              :x1="line.x1" :y1="line.y1" :x2="line.x2" :y2="line.y2"
              class="constellation-line" />
      </svg>
      <!-- 流星 -->
      <div class="meteor" :class="{ active: meteorActive }"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- Logo区域 -->
      <div class="login-header">
        <div class="logo-icon">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-svg">
            <!-- 月亮主体 - 呼吸动画 -->
            <path class="moon" d="M28 5C18 7 12 14 12 23C12 32 19 39 32 39C24 35 18 28 18 20C18 12 24 6 28 5Z" fill="currentColor" opacity="0.15"/>
            <path d="M28 5C18 7 12 14 12 23C12 32 19 39 32 39C24 35 18 28 18 20C18 12 24 6 28 5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
            <!-- 书籍 - 左侧翻开 -->
            <path d="M2 38V18C2 16.5 3 15.5 4.5 15.5H14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M2 38C2 39.5 3 40.5 4.5 40.5H14V15.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 38L14 15.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="currentColor" opacity="0.1"/>
            <!-- 书籍 - 右侧翻开 -->
            <path d="M46 38V18C46 16.5 45 15.5 43.5 15.5H34" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M46 38C46 39.5 45 40.5 43.5 40.5H34V15.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M46 38L34 15.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="currentColor" opacity="0.1"/>
            <!-- 书籍页面纹理 -->
            <path d="M5 20H11" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>
            <path d="M5 24H10" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>
            <path d="M5 28H9" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>
            <path d="M5 32H8" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>
            <path d="M43 20H37" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>
            <path d="M43 24H38" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>
            <path d="M43 28H39" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>
            <path d="M43 32H40" stroke="currentColor" stroke-width="1.2" opacity="0.6"/>
            <!-- 星辰 - 闪烁动画 -->
            <circle class="star star-1" cx="40" cy="8" r="1.5" fill="currentColor"/>
            <circle class="star star-2" cx="8" cy="10" r="1.2" fill="currentColor"/>
            <circle class="star star-3" cx="44" cy="14" r="0.8" fill="currentColor"/>
            <circle class="star star-4" cx="4" cy="14" r="0.9" fill="currentColor"/>
            <circle class="star star-5" cx="38" cy="4" r="0.6" fill="currentColor"/>
            <circle class="star star-6" cx="10" cy="6" r="0.7" fill="currentColor"/>
            <!-- 十字星 -->
            <g class="star-cross">
              <path d="M42 10L42 14" stroke="currentColor" stroke-width="0.8" stroke-linecap="round"/>
              <path d="M40 12L44 12" stroke="currentColor" stroke-width="0.8" stroke-linecap="round"/>
            </g>
          </svg>
        </div>
        <h1>学习系统</h1>
        <p>知识如星辰，照亮学习之路</p>
      </div>

      <!-- 角色切换 -->
      <div class="role-tabs">
        <div 
          class="role-tab" 
          :class="{ active: form.role === 'USER' }" 
          @click="form.role = 'USER'"
        >
          用户登录
        </div>
        <div 
          class="role-tab" 
          :class="{ active: form.role === 'ADMIN' }" 
          @click="form.role = 'ADMIN'"
        >
          管理员
        </div>
      </div>

      <!-- 登录表单 -->
      <el-form :model="form" :rules="rules" ref="formRef" class="login-form">
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
            @keyup.enter.native="login"
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button class="login-btn" @click="login">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部链接 -->
      <div class="login-footer">
        <span>还没有账号？</span>
        <a href="/register">立即注册</a>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 登录页面组件
 * 主题：知识星河 - 纯白背景 + 黑色星星装饰
 */
export default {
  name: "Login",
  
  data() {
    return {
      // 表单数据
      form: {
        username: '',
        password: '',
        role: 'USER'
      },
      // 验证规则
      rules: {
        username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
        password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
      },
      // 流星动画状态
      meteorActive: false,
      // 星座连线数据
      constellationLines: []
    }
  },
  
  mounted() {
    // 生成星座连线
    this.generateConstellation()
    // 启动流星动画
    this.startMeteor()
  },
  
  methods: {
    /**
     * 生成星星样式
     */
    getStarStyle(index) {
      const size = Math.random() * 3 + 1
      const x = Math.random() * 100
      const y = Math.random() * 100
      const opacity = Math.random() * 0.5 + 0.2
      const delay = Math.random() * 3
      
      return {
        width: size + 'px',
        height: size + 'px',
        left: x + '%',
        top: y + '%',
        opacity: opacity,
        animationDelay: delay + 's'
      }
    },
    
    /**
     * 生成星座连线
     */
    generateConstellation() {
      const lines = []
      const points = []
      
      // 生成随机星点
      for (let i = 0; i < 15; i++) {
        points.push({
          x: Math.random() * 1920,
          y: Math.random() * 1080
        })
      }
      
      // 连接部分星点
      for (let i = 0; i < points.length - 1; i++) {
        if (Math.random() > 0.4) {
          lines.push({
            x1: points[i].x,
            y1: points[i].y,
            x2: points[i + 1].x,
            y2: points[i + 1].y
          })
        }
      }
      
      this.constellationLines = lines
    },
    
    /**
     * 启动流星动画
     */
    startMeteor() {
      setInterval(() => {
        this.meteorActive = true
        setTimeout(() => {
          this.meteorActive = false
        }, 1000)
      }, 8000)
    },
    
    /**
     * 登录方法
     */
    login() {
      this.$refs['formRef'].validate((valid) => {
        if (valid) {
          this.$request.post('/login', this.form).then(res => {
            if (res.code === '200') {
              localStorage.setItem("xm-user", JSON.stringify(res.data))
              
              if (res.data.role === 'ADMIN') {
                this.$router.push('/home')
              } else {
                this.$router.push('/front/home')
              }
              
              this.$message.success('登录成功')
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
/* 页面容器 - 纯白背景 */
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  position: relative;
  overflow: hidden;
}

/* 星河背景层 */
.starfield {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

/* 星星 */
.stars {
  position: absolute;
  width: 100%;
  height: 100%;
}

.star {
  position: absolute;
  background: #1e293b;
  border-radius: 50%;
  animation: twinkle 3s infinite ease-in-out;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.6; }
}

/* 星座连线 */
.constellation {
  position: absolute;
  width: 100%;
  height: 100%;
}

.constellation-line {
  stroke: #e2e8f0;
  stroke-width: 1;
  opacity: 0.5;
}

/* 流星 */
.meteor {
  position: absolute;
  top: 10%;
  right: 20%;
  width: 2px;
  height: 80px;
  background: linear-gradient(to bottom, transparent, #1e293b, transparent);
  transform: rotate(-45deg);
  opacity: 0;
  transition: opacity 0.3s;
}

.meteor.active {
  animation: meteor-fall 1s ease-out forwards;
}

@keyframes meteor-fall {
  0% {
    opacity: 1;
    transform: rotate(-45deg) translateX(0);
  }
  100% {
    opacity: 0;
    transform: rotate(-45deg) translateX(-300px);
  }
}

/* 登录卡片 */
.login-card {
  width: 400px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  position: relative;
  z-index: 10;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

/* Logo区域 */
.login-header {
  text-align: center;
  padding: 40px 40px 24px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 20px;
  color: #1e293b;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: #64748b;
}

/* 角色切换 */
.role-tabs {
  display: flex;
  margin: 0 40px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.role-tab {
  flex: 1;
  padding: 12px 16px;
  text-align: center;
  font-size: 14px;
  color: #94a3b8;
  cursor: pointer;
  position: relative;
  transition: color 0.3s;
}

.role-tab:hover {
  color: #64748b;
}

.role-tab.active {
  color: #1e293b;
  font-weight: 500;
}

.role-tab.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 20%;
  right: 20%;
  height: 2px;
  background: #1e293b;
}

/* 表单 */
.login-form {
  padding: 0 40px 24px;
}

.login-form .el-form-item {
  margin-bottom: 20px;
}

.login-form .el-input__inner {
  height: 48px;
  padding-left: 40px;
  font-size: 14px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #1e293b;
}

.login-form .el-input__inner::placeholder {
  color: #94a3b8;
}

.login-form .el-input__inner:focus {
  border-color: #1e293b;
  background: #fff;
}

.login-form .el-input__prefix {
  left: 14px;
  font-size: 16px;
  color: #94a3b8;
}

/* 登录按钮 - 极简黑底白字 */
.login-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 500;
  background: #1e293b !important;
  border: none !important;
  border-radius: 8px !important;
  color: #fff !important;
  transition: all 0.3s ease !important;
}

.login-btn:hover {
  background: #000000 !important;
}

/* 底部链接 */
.login-footer {
  text-align: center;
  padding: 20px 40px 32px;
  border-top: 1px solid #f1f5f9;
  font-size: 14px;
  color: #94a3b8;
}

.login-footer a {
  color: #1e293b;
  font-weight: 500;
  margin-left: 4px;
  text-decoration: none;
  transition: color 0.3s;
}

.login-footer a:hover {
  color: #000000;
}

/* Logo动态图标动画 */
.logo-svg .moon {
  animation: moon-glow 3s ease-in-out infinite;
  transform-origin: center;
}

@keyframes moon-glow {
  0%, 100% { opacity: 0.15; }
  50% { opacity: 0.25; }
}

/* 星辰闪烁动画 */
.logo-svg .star {
  animation: star-twinkle 2s ease-in-out infinite;
}

.logo-svg .star-1 { animation-delay: 0s; }
.logo-svg .star-2 { animation-delay: 0.3s; }
.logo-svg .star-3 { animation-delay: 0.6s; }
.logo-svg .star-4 { animation-delay: 0.9s; }
.logo-svg .star-5 { animation-delay: 1.2s; }
.logo-svg .star-6 { animation-delay: 1.5s; }

@keyframes star-twinkle {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* 十字星闪烁 */
.logo-svg .star-cross {
  animation: cross-twinkle 2.5s ease-in-out infinite;
}

@keyframes cross-twinkle {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.9; }
}

/* 响应式 */
@media (max-width: 480px) {
  .login-card {
    width: 90%;
    margin: 20px;
  }
  
  .login-header {
    padding: 30px 30px 20px;
  }
  
  .role-tabs {
    margin: 0 30px 20px;
  }
  
  .login-form {
    padding: 0 30px 20px;
  }
  
  .login-footer {
    padding: 16px 30px 24px;
  }
}
</style>
