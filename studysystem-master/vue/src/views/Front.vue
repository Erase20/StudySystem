<template>
  <div class="front-layout">
    <!-- 公告栏 -->
    <div class="front-notice" v-if="top">
      <div class="notice-content">
        <i class="el-icon-bell"></i>
        <span class="notice-text">{{ top }}</span>
      </div>
    </div>
    
    <!-- 头部导航 -->
    <header class="front-header">
      <div class="header-container">
        <!-- Logo区域 -->
        <div class="header-left" @click="$router.push('/front/home')">
          <img src="@/assets/imgs/logo.png" alt="Logo" class="logo">
          <span class="brand-name">学习平台</span>
        </div>
        
        <!-- 导航菜单 -->
        <nav class="header-nav" :class="{ 'mobile-open': mobileMenuOpen }">
          <el-menu :default-active="$route.path" mode="horizontal" router>
            <el-menu-item index="/front/home">首页</el-menu-item>
            <el-menu-item index="/front/course">课程</el-menu-item>
            <el-menu-item index="/front/information">资源</el-menu-item>
            <el-menu-item index="/front/learningCenter">学习</el-menu-item>
            <el-menu-item index="/front/analysis">分析</el-menu-item>
          </el-menu>
        </nav>
        
        <!-- 右侧操作区 -->
        <div class="header-right">
          <!-- 移动端菜单按钮 -->
          <div class="mobile-menu-toggle" @click="mobileMenuOpen = !mobileMenuOpen">
            <i :class="mobileMenuOpen ? 'el-icon-close' : 'el-icon-menu'"></i>
          </div>

          <!-- 管理端入口 -->
          <el-button 
            v-if="user.role === 'ADMIN'" 
            type="text" 
            @click="goToAdmin" 
            class="admin-btn"
          >
            管理端
          </el-button>
          
          <!-- 未登录状态 -->
          <div v-if="!user.username" class="auth-buttons">
            <el-button class="login-btn" @click="$router.push('/login')">登录</el-button>
          </div>
          
          <!-- 已登录状态 -->
          <div v-else class="user-dropdown">
            <el-dropdown trigger="click" @command="handleCommand">
              <div class="user-info">
                <img :src="$getImageUrl(user.avatar) || require('@/assets/imgs/logo.png')" alt="头像" class="user-avatar">
                <span class="user-name">{{ user.name }}</span>
                <i class="el-icon-arrow-down"></i>
              </div>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="/front/person">个人中心</el-dropdown-item>
                <el-dropdown-item command="/front/learningCenter">我的学习</el-dropdown-item>
                <el-dropdown-item command="/front/analysis">学习分析</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </div>
      </div>
    </header>
    
    <!-- 主体内容 -->
    <main class="main-body">
      <router-view ref="child" @update:user="updateUser" />
    </main>

    <!-- 页脚 -->
    <Footer />
  </div>
</template>

<script>
/**
 * 前台布局组件
 * 包含导航栏、公告栏、主体内容区
 */
import Footer from '@/components/common/Footer.vue'

export default {
  name: "FrontLayout",
  components: { Footer },
  
  data() {
    return {
      top: '',
      notice: [],
      user: JSON.parse(localStorage.getItem("xm-user") || '{}'),
      mobileMenuOpen: false
    }
  },
  
  mounted() {
    this.loadNotice()
  },
  
  methods: {
    /**
     * 加载公告
     */
    loadNotice() {
      this.$request.get('/notice/selectAll').then(res => {
        this.notice = res.data || []
        if (this.notice.length > 0) {
          let i = 0
          this.top = this.notice[0].content
          setInterval(() => {
            this.top = this.notice[i].content
            i = (i + 1) % this.notice.length
          }, 3000)
        }
      }).catch(() => {})
    },
    
    /**
     * 更新用户信息
     */
    updateUser() {
      this.user = JSON.parse(localStorage.getItem('xm-user') || '{}')
    },
    
    /**
     * 处理下拉菜单命令
     */
    handleCommand(command) {
      if (command === 'logout') {
        this.logout()
      } else {
        this.$router.push(command)
        this.mobileMenuOpen = false
      }
    },
    
    /**
     * 退出登录
     */
    logout() {
      localStorage.removeItem("xm-user")
      this.$router.push("/login")
    },
    
    /**
     * 跳转管理端
     */
    goToAdmin() {
      this.$router.push('/home')
    }
  }
}
</script>

<style scoped>
/* 公告栏 */
.front-notice {
  background: #1e293b;
  padding: 8px 0;
  text-align: center;
}

.notice-content {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 13px;
}

.notice-content i {
  font-size: 14px;
}

.notice-text {
  opacity: 0.9;
}

/* 头部导航 */
.front-header {
  background: #fff;
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid #e2e8f0;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  height: 60px;
  padding: 0 24px;
}

/* Logo区域 */
.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  margin-right: 40px;
}

.logo {
  width: 32px;
  height: 32px;
  border-radius: 8px;
}

.brand-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* 导航菜单 */
.header-nav {
  flex: 1;
}

.header-nav .el-menu {
  background: transparent !important;
  border: none !important;
  height: 60px;
}

.header-nav .el-menu-item {
  height: 60px !important;
  line-height: 60px !important;
  padding: 0 20px !important;
  font-size: 14px !important;
  color: #64748b !important;
  background: transparent !important;
  border-bottom: 2px solid transparent !important;
}

.header-nav .el-menu-item:hover {
  color: #1e293b !important;
  background: transparent !important;
}

.header-nav .el-menu-item.is-active {
  color: #1e293b !important;
  border-bottom: 2px solid #1e293b !important;
  background: transparent !important;
}

/* 右侧操作区 */
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-btn {
  color: #64748b;
  font-size: 14px;
}

.admin-btn:hover {
  color: #1e293b;
}

/* 登录按钮 - 极简黑底 */
.login-btn {
  background: #1e293b !important;
  border: none !important;
  color: #fff !important;
  padding: 8px 20px !important;
  border-radius: 6px !important;
  font-size: 14px !important;
}

.login-btn:hover {
  background: #000 !important;
}

/* 用户下拉 */
.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 8px;
  transition: background 0.3s;
}

.user-info:hover {
  background: #f8fafc;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-size: 14px;
  color: #1e293b;
}

.user-info .el-icon-arrow-down {
  font-size: 12px;
  color: #94a3b8;
}

/* 下拉菜单 */
:deep(.el-dropdown-menu) {
  padding: 8px 0 !important;
  border-radius: 8px !important;
  border: 1px solid #e2e8f0 !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
}

:deep(.el-dropdown-menu__item) {
  padding: 10px 20px !important;
  font-size: 14px !important;
  color: #475569 !important;
}

:deep(.el-dropdown-menu__item:hover) {
  background: #f8fafc !important;
  color: #1e293b !important;
}

/* 主体内容 */
.main-body {
  min-height: calc(100vh - 60px);
  background: #fff;
}

/* 响应式 */
@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
   }
  
  .header-left {
    margin-right: 16px;
  }
  
  .brand-name {
    display: none;
  }
  
  .header-nav {
    display: none;
  }

  /* 移动端汉堡菜单 */
  .header-nav.mobile-open {
    display: block;
    position: absolute;
    top: 60px;
    left: 0;
    right: 0;
    background: #fff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    z-index: 999;
    padding: 8px 0;
  }

  .header-nav.mobile-open .el-menu {
    display: flex;
    flex-direction: column;
    height: auto;
  }

  .header-nav.mobile-open .el-menu-item {
    height: 48px !important;
    line-height: 48px !important;
    padding: 0 24px !important;
    border-bottom: none !important;
  }
  
  .user-name {
    display: none;
  }
  
  .admin-btn {
    display: none;
  }

  .mobile-menu-toggle {
    display: flex;
  }
}

/* 移动端菜单按钮 - 默认隐藏 */
.mobile-menu-toggle {
  display: none;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #1e293b;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
  margin-right: 8px;
}

.mobile-menu-toggle:hover {
  background: #f1f5f9;
}
</style>
