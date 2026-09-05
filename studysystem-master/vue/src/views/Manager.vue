<template>
  <div class="manager-container" :class="{ 'sidebar-collapsed': isCollapsed }">
    <!--  头部  -->
    <div class="manager-header">
      <div class="manager-header-left">
        <img src="@/assets/imgs/logo.png" />
        <div class="title" v-show="!isCollapsed">后台管理系统</div>
        <div class="collapse-btn" @click="isCollapsed = !isCollapsed">
          <i :class="isCollapsed ? 'el-icon-s-unfold' : 'el-icon-s-fold'"></i>
        </div>
      </div>

      <div class="manager-header-center">
        <el-breadcrumb separator-class="el-icon-arrow-right">
          <el-breadcrumb-item :to="{ path: '/home' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: $route.path }">{{ $route.meta.name }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <div class="manager-header-right">
        <!-- 返回前台按钮 -->
        <el-button 
          type="text" 
          @click="goToFront" 
          class="switch-btn"
          style="margin-right: 16px;"
        >
          <i class="el-icon-s-shop"></i> 前台首页
        </el-button>
        
        <el-dropdown placement="bottom">
          <div class="avatar">
            <img :src="$getImageUrl(user.avatar) || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
            <div>{{ user.name ||  '管理员' }}</div>
          </div>
          <el-dropdown-menu slot="dropdown">
            <el-dropdown-item @click.native="goToPerson">个人信息</el-dropdown-item>
            <el-dropdown-item @click.native="$router.push('/password')">修改密码</el-dropdown-item>
            <el-dropdown-item @click.native="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </el-dropdown>
      </div>
    </div>

    <!--  主体  -->
    <div class="manager-main">
      <!--  侧边栏  -->
      <div class="manager-main-left" :class="{ 'sidebar-collapsed-left': isCollapsed }">
        <el-menu 
          :default-openeds="isCollapsed ? [] : ['content', 'order', 'user']" 
          router 
          style="border: none" 
          :default-active="$route.path"
          :collapse="isCollapsed"
          :collapse-transition="true"
        >
          <el-menu-item index="/home">
            <i class="el-icon-s-home"></i>
            <span slot="title">系统首页</span>
          </el-menu-item>
          <el-submenu index="content">
            <template slot="title">
              <i class="el-icon-reading"></i><span>内容管理</span>
            </template>
            <el-menu-item index="/course"><i class="el-icon-video-camera"></i><span>课程信息</span></el-menu-item>
            <el-menu-item index="/information"><i class="el-icon-document"></i><span>资料审核</span></el-menu-item>
            <el-menu-item index="/notice"><i class="el-icon-bell"></i><span>公告信息</span></el-menu-item>
            <el-menu-item index="/score"><i class="el-icon-trophy"></i><span>积分专区</span></el-menu-item>
          </el-submenu>
          <el-submenu index="order">
            <template slot="title">
              <i class="el-icon-s-order"></i><span>订单中心</span>
            </template>
            <el-menu-item index="/orders"><i class="el-icon-shopping-cart-2"></i><span>课程订单</span></el-menu-item>
            <el-menu-item index="/scoreOrder"><i class="el-icon-coin"></i><span>积分兑课</span></el-menu-item>
            <el-menu-item index="/fileOrder"><i class="el-icon-download"></i><span>资料下载</span></el-menu-item>
            <el-menu-item index="/record"><i class="el-icon-wallet"></i><span>充值记录</span></el-menu-item>
          </el-submenu>
          <el-submenu index="user">
            <template slot="title">
              <i class="el-icon-user"></i><span>用户管理</span>
            </template>
            <el-menu-item index="/admin"><i class="el-icon-s-custom"></i><span>管理员信息</span></el-menu-item>
            <el-menu-item index="/user"><i class="el-icon-user-solid"></i><span>用户信息</span></el-menu-item>
          </el-submenu>
          <el-submenu index="analysis">
            <template slot="title">
              <i class="el-icon-data-analysis"></i><span>算法分析</span>
            </template>
            <el-menu-item index="/userCluster"><i class="el-icon-s-data"></i><span>用户聚类分析</span></el-menu-item>
            <el-menu-item index="/sentiment"><i class="el-icon-chat-dot-round"></i><span>评论情感分析</span></el-menu-item>
          </el-submenu>
          <el-submenu index="system">
            <template slot="title">
              <i class="el-icon-setting"></i><span>系统设置</span>
            </template>
            <el-menu-item index="/adminPerson"><i class="el-icon-s-tools"></i><span>个人信息</span></el-menu-item>
            <el-menu-item index="/password"><i class="el-icon-lock"></i><span>修改密码</span></el-menu-item>
          </el-submenu>
        </el-menu>
      </div>

      <!--  数据表格  -->
      <div class="manager-main-right">
        <router-view @update:user="updateUser" />
      </div>
    </div>

    <!-- 移动端遮罩 -->
    <div class="sidebar-overlay" v-if="isMobileMenuOpen" @click="isMobileMenuOpen = false"></div>
    <!-- 移动端菜单按钮 -->
    <div class="mobile-menu-btn" @click="isMobileMenuOpen = !isMobileMenuOpen" v-if="isMobile">
      <i class="el-icon-menu"></i>
    </div>
  </div>
</template>

<script>
export default {
  name: "Manager",
  data() {
    return {
      user: JSON.parse(localStorage.getItem('xm-user') || '{}'),
      isCollapsed: false,
      isMobile: false,
      isMobileMenuOpen: false,
    }
  },
  created() {
    if (!this.user.id) {
      this.$router.push('/login')
    }
    this.checkMobile()
    window.addEventListener('resize', this.checkMobile)
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.checkMobile)
  },
  methods: {
    checkMobile() {
      this.isMobile = window.innerWidth <= 768
      if (this.isMobile) {
        this.isCollapsed = false
      }
    },
    updateUser() {
      this.user = JSON.parse(localStorage.getItem('xm-user') || '{}')
    },
    goToPerson() {
      if (this.user.role === 'ADMIN') {
        this.$router.push('/adminPerson')
      }
    },
    logout() {
      localStorage.removeItem('xm-user')
      this.$router.push('/login')
    },
    goToFront() {
      this.$router.push('/front/home')
    }
  }
}
</script>

<style scoped>
@import "@/assets/css/manager.css";
</style>