import request from '@/utils/request'

// 积分课程相关 API
export const scoreApi = {
  // 获取积分课程列表
  getList(params) {
    return request.get('/score/selectPage', { params })
  },
  // 获取积分课程详情
  getDetail(id) {
    return request.get('/score/selectById?id=' + id)
  },
  // 获取推荐积分课程
  getRecommend() {
    return request.get('/score/getRecommend')
  },
  // 获取热门积分课程
  getTop8() {
    return request.get('/score/getTop8')
  }
}

export default scoreApi