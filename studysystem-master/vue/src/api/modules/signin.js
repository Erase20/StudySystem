import request from '@/utils/request'

// 签到相关 API
export const signinApi = {
  // 获取签到记录
  getByUserId(userId) {
    return request.get('/signin/selectByUserId?id=' + userId)
  },
  // 签到
  signin(data) {
    return request.post('/signin/add', data)
  }
}

export default signinApi