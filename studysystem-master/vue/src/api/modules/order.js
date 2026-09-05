import request from '@/utils/request'

// 订单相关 API
export const orderApi = {
  // 创建订单
  create(data) {
    return request.post('/orders/add', data)
  },
  // 获取用户订单
  getUserOrders(userId) {
    return request.get('/orders/selectByUserId?userId=' + userId)
  },
  // 获取积分兑换订单
  getScoreOrders(userId) {
    return request.get('/scoreorder/selectByUserId?userId=' + userId)
  },
  // 获取下载记录
  getFileOrders(userId) {
    return request.get('/fileorder/selectByUserId?userId=' + userId)
  }
}

export default orderApi