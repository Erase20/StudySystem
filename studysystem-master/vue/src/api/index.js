// 导入各模块API
import courseApi from './modules/course'
import scoreApi from './modules/score'
import infoApi from './modules/information'
import userApi from './modules/user'
import orderApi from './modules/order'
import signinApi from './modules/signin'
import noticeApi from './modules/notice'
import commentApi from './modules/comment'

// 导出所有API
export {
  courseApi,
  scoreApi,
  infoApi,
  userApi,
  orderApi,
  signinApi,
  noticeApi,
  commentApi
}

// 默认导出，保持与原来的使用方式一致
export default {
  course: courseApi,
  score: scoreApi,
  info: infoApi,
  user: userApi,
  order: orderApi,
  signin: signinApi,
  notice: noticeApi,
  comment: commentApi
}