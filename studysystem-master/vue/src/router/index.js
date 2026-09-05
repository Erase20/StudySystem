/**
 * Vue Router 路由配置文件
 * 作用：定义应用的所有路由规则，实现页面导航和权限控制
 */

import Vue from 'vue'
import VueRouter from 'vue-router'
import { managerRoutes } from './modules/manager'   // 后台管理路由
import { frontRoutes } from './modules/front'       // 前台页面路由

// 注册VueRouter插件，使组件可以使用 this.$router
Vue.use(VueRouter)

// ==================== 解决Vue Router 3.0+ 重复导航报错问题 ====================
// 问题：频繁点击菜单会抛出 "NavigationDuplicated" 错误
// 解决：重写push方法，捕获错误但不抛出
const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push (location) {
  return originalPush.call(this, location).catch(err => err)
}

// ==================== 路由配置 ====================
const routes = [
  // 后台管理路由组
  {
    path: '/',                          // 根路径
    name: 'Manager',
    component: () => import('../views/Manager.vue'),  // 懒加载，按需加载组件
    redirect: '/home',                  // 访问/时重定向到/home
    children: managerRoutes             // 子路由（在modules/manager.js中定义）
  },
  // 前台展示路由组
  {
    path: '/front',
    name: 'Front',
    component: () => import('../views/Front.vue'),
    children: frontRoutes
  },
  // 登录页面
  { 
    path: '/login', 
    name: 'Login', 
    meta: { name: '登录' },              // 路由元信息，可用于面包屑、标题等
    component: () => import('../views/Login.vue') 
  },
  // 注册页面
  { 
    path: '/register', 
    name: 'Register', 
    meta: { name: '注册' }, 
    component: () => import('../views/Register.vue') 
  },
  // 404页面（匹配所有未定义的路由）
  { 
    path: '*',                          // 通配符，匹配所有路径
    name: 'NotFound', 
    meta: { name: '无法访问' }, 
    component: () => import('../views/404.vue') 
  },
]

// 创建路由实例
const router = new VueRouter({
  mode: 'history',                      // 使用HTML5 History模式（URL无#号）
  base: process.env.BASE_URL,           // 应用基础URL
  routes                               // 路由配置数组
})

// ==================== 全局路由守卫（权限控制核心）====================
/**
 * router.beforeEach: 在路由跳转前执行
 * 参数说明：
 *   to: 目标路由对象
 *   from: 来源路由对象
 *   next: 控制跳转的函数
 *     - next(): 放行，继续跳转
 *     - next('/path'): 重定向到指定路径
 *     - next(false): 取消跳转
 */
router.beforeEach((to, from, next) => {
  // 从localStorage获取登录用户信息（登录时存储）
  const user = JSON.parse(localStorage.getItem('xm-user') || '{}')
  
  // 1. 登录和注册页面不需要校验，直接放行
  if (to.path === '/login' || to.path === '/register') {
    next()
    return
  }
  
  // 2. 未登录用户权限控制
  if (!user.id) {
    // 未登录只能访问前台页面（/front开头）
    if (to.path.startsWith('/front')) {
      next()          // 放行
    } else {
      next('/login')  // 重定向到登录页
    }
    return
  }
  
  // 3. 已登录用户权限控制
  if (to.path.startsWith('/front')) {
    // 前台页面所有登录用户都可以访问
    next()
  } else {
    // 后台管理页面只有管理员可以访问
    if (user.role === 'ADMIN') {
      next()
    } else {
      next('/front/home')  // 普通用户重定向到前台首页
    }
  }
})

export default router
