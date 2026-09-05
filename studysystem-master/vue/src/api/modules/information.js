import request from '@/utils/request'

// 资料相关 API
export const infoApi = {
  // 获取资料列表
  getList(params) {
    return request.get('/information/selectPage', { params })
  },
  // 获取资料详情
  getDetail(id) {
    return request.get('/information/selectById?id=' + id)
  },
  // 获取推荐资料
  getRecommend() {
    return request.get('/information/getRecommend')
  },
  // 获取热门资料
  getTop8() {
    return request.get('/information/selectTop8')
  }
}

export default infoApi