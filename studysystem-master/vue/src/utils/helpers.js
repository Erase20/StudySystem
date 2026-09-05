/**
 * 工具函数集合
 */

// ==================== 日期时间相关 ====================

/**
 * 格式化日期
 * @param {string|Date} date - 日期
 * @param {string} format - 格式，默认 YYYY-MM-DD
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return ''
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hour = String(d.getHours()).padStart(2, '0')
  const minute = String(d.getMinutes()).padStart(2, '0')
  const second = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}

/**
 * 获取相对时间描述
 * @param {string|Date} date - 日期
 */
export function getRelativeTime(date) {
  if (!date) return ''
  const now = new Date()
  const target = new Date(date)
  const diff = now - target
  
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day
  
  if (diff < minute) return '刚刚'
  if (diff < hour) return Math.floor(diff / minute) + '分钟前'
  if (diff < day) return Math.floor(diff / hour) + '小时前'
  if (diff < week) return Math.floor(diff / day) + '天前'
  return formatDate(date)
}

// ==================== 字符串相关 ====================

/**
 * 截断文本
 * @param {string} text - 文本
 * @param {number} length - 最大长度
 * @param {string} suffix - 后缀，默认 ...
 */
export function truncate(text, length = 50, suffix = '...') {
  if (!text) return ''
  if (text.length <= length) return text
  return text.substring(0, length) + suffix
}

/**
 * 首字母大写
 * @param {string} str - 字符串
 */
export function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1)
}

// ==================== 数值相关 ====================

/**
 * 格式化金额
 * @param {number} amount - 金额
 * @param {number} decimals - 小数位
 */
export function formatMoney(amount, decimals = 2) {
  if (amount === null || amount === undefined) return '0.00'
  return Number(amount).toFixed(decimals)
}

/**
 * 格式化数字（千分位）
 * @param {number} num - 数字
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '0'
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// ==================== 文件相关 ====================

/**
 * 获取文件扩展名
 * @param {string} filename - 文件名
 */
export function getFileExt(filename) {
  if (!filename) return ''
  const ext = filename.split('.').pop()
  return ext.toLowerCase()
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// ==================== 验证相关 ====================

/**
 * 验证手机号
 * @param {string} phone - 手机号
 */
export function isValidPhone(phone) {
  return /^1[3-9]\d{9}$/.test(phone)
}

/**
 * 验证邮箱
 * @param {string} email - 邮箱
 */
export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

/**
 * 验证身份证号
 * @param {string} idCard - 身份证号
 */
export function isValidIdCard(idCard) {
  return /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/.test(idCard)
}

// ==================== 存储相关 ====================

/**
 * 获取本地存储的用户信息
 */
export function getUserInfo() {
  try {
    return JSON.parse(localStorage.getItem('xm-user') || '{}')
  } catch {
    return {}
  }
}

/**
 * 设置本地存储的用户信息
 * @param {object} user - 用户信息
 */
export function setUserInfo(user) {
  localStorage.setItem('xm-user', JSON.stringify(user))
}

/**
 * 清除用户信息
 */
export function clearUserInfo() {
  localStorage.removeItem('xm-user')
}

// ==================== 路由相关 ====================

/**
 * 跳转到课程详情
 * @param {number} id - 课程ID
 * @param {boolean} isScore - 是否积分课程
 */
export function navToCourse(id, isScore = false) {
  const path = isScore ? '/front/scoreDetail' : '/front/courseDetail'
  return { path, query: { id } }
}

/**
 * 跳转到资料详情
 * @param {number} id - 资料ID
 */
export function navToInfo(id) {
  return { path: '/front/informationDetail', query: { id } }
}

// ==================== 防抖节流 ====================

/**
 * 防抖函数
 * @param {Function} fn - 原函数
 * @param {number} delay - 延迟时间
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn - 原函数
 * @param {number} interval - 间隔时间
 */
export function throttle(fn, interval = 300) {
  let lastTime = 0
  return function (...args) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

// ==================== 颜色相关 ====================

/**
 * 生成随机颜色
 */
export function randomColor() {
  return '#' + Math.floor(Math.random() * 16777215).toString(16)
}

/**
 * 颜色转RGB
 * @param {string} color - 颜色值
 */
export function hexToRgb(color) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(color)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null
}

// ==================== URL相关 ====================

/**
 * 解析URL参数
 * @param {string} url - URL地址
 */
export function parseUrlParams(url = window.location.href) {
  const search = url.split('?')[1]
  if (!search) return {}
  
  return search.split('&').reduce((params, param) => {
    const [key, value] = param.split('=')
    params[key] = decodeURIComponent(value)
    return params
  }, {})
}

/**
 * 构建URL参数
 * @param {object} params - 参数对象
 */
export function buildUrlParams(params) {
  if (!params) return ''
  
  const searchParams = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      searchParams.append(key, value)
    }
  })
  
  const search = searchParams.toString()
  return search ? '?' + search : ''
}

// ==================== 数组相关 ====================

/**
 * 数组去重
 * @param {array} arr - 原数组
 */
export function uniqueArray(arr) {
  return [...new Set(arr)]
}

/**
 * 数组随机排序
 * @param {array} arr - 原数组
 */
export function shuffleArray(arr) {
  const newArr = [...arr]
  for (let i = newArr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[newArr[i], newArr[j]] = [newArr[j], newArr[i]]
  }
  return newArr
}

/**
 * 数组分组
 * @param {array} arr - 原数组
 * @param {number} size - 每组大小
 */
export function chunkArray(arr, size) {
  const result = []
  for (let i = 0; i < arr.length; i += size) {
    result.push(arr.slice(i, i + size))
  }
  return result
}

// ==================== 对象相关 ====================

/**
 * 深拷贝对象
 * @param {object} obj - 原对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (typeof obj === 'object') {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}

/**
 * 对象合并
 * @param {object} target - 目标对象
 * @param {object} source - 源对象
 */
export function mergeObjects(target, source) {
  return { ...target, ...source }
}

// ==================== 安全相关 ====================

/**
 * 转义HTML
 * @param {string} str - 原始字符串
 */
export function escapeHtml(str) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  return str.replace(/[&<>"]/g, m => map[m])
}

/**
 * 生成随机字符串
 * @param {number} length - 字符串长度
 */
export function randomString(length = 10) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

export default {
  formatDate,
  getRelativeTime,
  truncate,
  capitalize,
  formatMoney,
  formatNumber,
  getFileExt,
  formatFileSize,
  isValidPhone,
  isValidEmail,
  isValidIdCard,
  getUserInfo,
  setUserInfo,
  clearUserInfo,
  navToCourse,
  navToInfo,
  debounce,
  throttle,
  randomColor,
  hexToRgb,
  parseUrlParams,
  buildUrlParams,
  uniqueArray,
  shuffleArray,
  chunkArray,
  deepClone,
  mergeObjects,
  escapeHtml,
  randomString
}
