import request from '@/utils/request'

// 课程相关 API
export const courseApi = {
  // 获取课程列表
  getList(params) {
    return request.get('/course/selectPage', { params })
  },
  // 获取课程详情
  getDetail(id) {
    return request.get('/course/selectById?id=' + id)
  },
  // 获取推荐课程
  getRecommend(type) {
    return request.get('/course/getRecommend?type=' + type)
  },
  // 获取热门课程
  getTop8(type) {
    return request.get('/course/selectTop8?type=' + type)
  },
  // 协同过滤推荐
  getRecommendCourses(limit = 8) {
    return request.get('/course/recommend?limit=' + limit)
  },
  // 智能推荐
  getSmartRecommend(limit = 8) {
    return request.get('/analysis/smart-recommend?limit=' + limit)
  }
}

export default courseApi