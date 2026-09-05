<template>
  <header class="header">
    <div class="header-container">
      <!-- 左侧Logo -->
      <div class="logo" @click="navToHome">
        <img src="@/assets/imgs/logo.png" alt="Logo" class="logo-img">
        <span class="logo-text">在线学习平台</span>
      </div>
      
      <!-- 中间导航菜单 -->
      <nav class="nav-menu">
        <a href="/front" class="nav-item" :class="{ active: isActive('/front') }">首页</a>
        <a href="/front/course" class="nav-item" :class="{ active: isActive('/front/course') }">课程</a>
        <a href="/front/information" class="nav-item" :class="{ active: isActive('/front/information') }">资料</a>
        <a href="/front/learningCenter" class="nav-item" :class="{ active: isActive('/front/learningCenter') }">学习中心</a>
        <a href="/front/dataAnalysis" class="nav-item" :class="{ active: isActive('/front/dataAnalysis') }">数据分析</a>
      </nav>
      
      <!-- 右侧用户操作 -->
      <div class="user-actions">
        <div v-if="isLoggedIn" class="user-info">
          <span class="welcome">欢迎, {{ username }}</span>
          <el-dropdown trigger="click">
            <span class="user-avatar">
              <img :src="userAvatar" alt="Avatar" class="avatar-img">
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item @click="navToPerson">个人中心</el-dropdown-item>
              <el-dropdown-item @click="navToOrders">我的订单</el-dropdown-item>
              <el-dropdown-item @click="navToScore">我的积分</el-dropdown-item>
              <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
        <div v-else class="login-register">
          <a href="/login" class="action-btn">登录</a>
          <a href="/register" class="action-btn primary">注册</a>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
export default {
  computed: {
    isLoggedIn() {
      return this.$store.getters['user/isLoggedIn']
    },
    username() {
      return this.$store.getters['user/username']
    },
    userAvatar() {
      const userInfo = this.$store.getters['user/userInfo']
      return userInfo.avatar || require('@/assets/imgs/logo.png')
    }
  },
  methods: {
    isActive(path) {
      return this.$route.path.startsWith(path)
    },
    navToHome() {
      this.$router.push('/front')
    },
    navToPerson() {
      this.$router.push('/front/person')
    },
    navToOrders() {
      this.$router.push('/front/orders')
    },
    navToScore() {
      this.$router.push('/front/score')
    },
    logout() {
      this.$store.dispatch('user/logout')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 12px;
}

.logo-img {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

/* 导航菜单 */
.nav-menu {
  display: flex;
  gap: 32px;
}

.nav-item {
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: color 0.3s;
  position: relative;
}

.nav-item:hover {
  color: #1e293b;
}

.nav-item.active {
  color: #1e293b;
  font-weight: 600;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #1e293b;
}

/* 用户操作 */
.user-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.login-register {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #f1f5f9;
}

.action-btn.primary {
  background: #1e293b;
  color: #fff;
}

.action-btn.primary:hover {
  background: #000;
  color: #fff;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.welcome {
  font-size: 14px;
  color: #64748b;
}

.user-avatar {
  cursor: pointer;
}

.avatar-img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

/* 响应式 */
@media (max-width: 900px) {
  .nav-menu {
    gap: 24px;
  }
  
  .user-info {
    gap: 12px;
  }
  
  .welcome {
    display: none;
  }
}

@media (max-width: 600px) {
  .header-container {
    padding: 0 16px;
  }
  
  .logo-text {
    font-size: 16px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .login-register {
    gap: 8px;
  }
  
  .action-btn {
    padding: 4px 12px;
    font-size: 13px;
  }
}
</style>