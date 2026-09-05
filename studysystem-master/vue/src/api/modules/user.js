import request from '@/utils/request'

// 用户相关 API
export const userApi = {
  // 登录
  login(data) {
    return request.post('/login', data)
  },
  // 注册
  register(data) {
    return request.post('/register', data)
  },
  // 获取用户信息
  getInfo(id) {
    return request.get('/user/selectById?id=' + id)
  },
  // 更新用户信息
  update(data) {
    return request.put('/user/update', data)
  },
  // 修改密码
  updatePassword(data) {
    return request.put('/user/updatePassword', data)
  }
}

export default userApi