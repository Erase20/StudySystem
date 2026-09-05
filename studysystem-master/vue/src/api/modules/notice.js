import request from '@/utils/request'

// 公告相关 API
export const noticeApi = {
  // 获取所有公告
  getAll() {
    return request.get('/notice/selectAll')
  }
}

export default noticeApi