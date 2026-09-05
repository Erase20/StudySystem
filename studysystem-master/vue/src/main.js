/**
 * Vue应用入口文件
 * 作用：初始化Vue实例，加载插件、全局配置和样式
 */

import Vue from 'vue'                          // 引入Vue核心库
import App from './App.vue'                    // 引入根组件
import router from './router'                  // 引入路由配置
import store from './store'                    // 引入Vuex状态管理
import ElementUI from 'element-ui'             // 引入Element UI组件库
import 'element-ui/lib/theme-chalk/index.css'  // 引入Element UI默认样式
import '@/assets/css/global.css'               // 引入全局自定义样式
import '@/assets/css/theme/index.css'          // 引入主题样式
import request from "@/utils/request";          // 引入封装的axios请求工具

// 关闭生产环境提示（减少控制台输出）
Vue.config.productionTip = false

// ==================== 全局挂载（所有组件可通过this访问）====================

// 将request挂载到Vue原型，组件中通过 this.$request 调用
Vue.prototype.$request = request

// 将后端基础URL挂载到Vue原型，组件中通过 this.$baseUrl 访问
Vue.prototype.$baseUrl = process.env.VUE_APP_BASEURL

// 全局图片URL处理方法：自动处理外部防盗链图片
// 外部图片走后端代理（/proxy/image?url=xxx），本地图片正常拼接
Vue.prototype.$getImageUrl = function(img) {
  if (!img) return ''
  // 本地文件路径（以 /files/ 开头）
  if (img.startsWith('/files/')) {
    return this.$baseUrl + img
  }
  // 外部URL（http/https），走后端代理绕过防盗链
  if (img.startsWith('http://') || img.startsWith('https://')) {
    return this.$baseUrl + '/proxy/image?url=' + encodeURIComponent(img)
  }
  // 其他情况，尝试拼为本地文件
  return this.$baseUrl + '/files/' + img
}

// ==================== 插件配置 ====================

// 注册Element UI插件，全局配置组件默认size为small
Vue.use(ElementUI, {size: "small"})

// ==================== 创建Vue实例 ====================

new Vue({
    router,     // 注入路由实例，使组件可以使用 this.$router 和 this.$route
    store,      // 注入Vuex状态管理，使组件可以使用 this.$store
    render: h => h(App)  // 渲染函数：将App组件渲染到DOM中
}).$mount('#app')  // 挂载到id为app的DOM元素上（public/index.html中定义）
