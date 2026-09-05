import request from '@/utils/request'

// 评论相关 API
export const commentApi = {
  // 获取课程评论
  getByCourseId(courseId) {
    return request.get('/comment/selectByCourseId?courseId=' + courseId)
  },
  // 添加评论
  add(data) {
    return request.post('/comment/add', data)
  }
}

export default commentApi