/**
 * Axios请求封装模块
 * 作用：统一处理请求配置、请求拦截、响应拦截
 * 好处：
 *   1. 统一配置baseURL和超时时间
 *   2. 自动添加token到请求头
 *   3. 统一处理响应结果和错误
 *   4. 简化组件中的请求代码
 */

import axios from 'axios'
import router from "@/router";  // 导入路由实例，用于跳转

// ==================== 创建axios实例 ====================
const request = axios.create({
    baseURL: process.env.VUE_APP_BASEURL,   // 后端接口基础地址，从环境变量读取
    timeout: 30000                          // 请求超时时间：30秒
})

// ==================== 请求拦截器 ====================
/**
 * 作用：在请求发送前统一处理请求配置
 * 应用场景：
 *   - 添加认证token
 *   - 设置请求头
 *   - 参数加密/序列化
 *   - 显示loading
 */
request.interceptors.request.use(
    // 请求发送前的处理函数
    config => {
        // 1. 设置请求内容类型为JSON
        config.headers['Content-Type'] = 'application/json;charset=utf-8';
        
        // 2. 从localStorage获取用户信息，提取token
        // localStorage是浏览器本地存储，登录成功后将用户信息存储在此
        let user = JSON.parse(localStorage.getItem("xm-user") || '{}')
        
        // 3. 将token添加到请求头，后端通过此token识别用户身份
        config.headers['token'] = user.token

        return config  // 必须返回config，请求才会继续
    },
    // 请求发生错误的处理函数
    error => {
        console.error('request error: ' + error)  // 打印错误便于调试
        return Promise.reject(error)  // 将错误传递给调用方
    }
);

// ==================== 响应拦截器 ====================
/**
 * 作用：在接收到响应后统一处理响应结果
 * 应用场景：
 *   - 统一处理错误码
 *   - 未登录时自动跳转登录页
 *   - 数据格式转换
 *   - 隐藏loading
 */
request.interceptors.response.use(
    // 响应成功的处理函数（HTTP状态码2xx）
    response => {
        let res = response.data;  // 获取后端返回的数据

        // 1. 兼容服务端返回的字符串格式数据（转为JSON）
        if (typeof res === 'string') {
            res = res ? JSON.parse(res) : res
        }
        
        // 2. 处理401未登录状态
        // 当后端返回code为401时，说明token过期或无效，跳转到登录页
        if (res.code === '401') {
            router.push('/login')
        }
        
        return res;  // 返回处理后的数据给调用方
    },
    // 响应错误的处理函数（HTTP状态码非2xx）
    error => {
        console.error('response error: ' + error)
        return Promise.reject(error)
    }
)

// 导出封装好的请求对象，供其他模块使用
export default request