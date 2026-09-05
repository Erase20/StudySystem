/**
 * 后台管理路由配置
 */
export const managerRoutes = [
  { path: '403', name: 'Manager403', meta: { name: '无权限' }, component: () => import('@/views/manager/common/403') },
  { path: 'home', name: 'ManagerHome', meta: { name: '系统首页' }, component: () => import('@/views/manager/home/Home') },
  { path: 'admin', name: 'Admin', meta: { name: '管理员信息' }, component: () => import('@/views/manager/user/Admin') },
  { path: 'user', name: 'User', meta: { name: '用户信息' }, component: () => import('@/views/manager/user/User') },
  { path: 'adminPerson', name: 'AdminPerson', meta: { name: '个人信息' }, component: () => import('@/views/manager/user/AdminPerson') },
  { path: 'password', name: 'Password', meta: { name: '修改密码' }, component: () => import('@/views/manager/user/Password') },
  { path: 'notice', name: 'Notice', meta: { name: '公告信息' }, component: () => import('@/views/manager/notice/Notice') },
  { path: 'course', name: 'Course', meta: { name: '课程信息' }, component: () => import('@/views/manager/course/Course') },
  { path: 'score', name: 'Score', meta: { name: '积分专区' }, component: () => import('@/views/manager/score/Score') },
  { path: 'information', name: 'Information', meta: { name: '资料审核' }, component: () => import('@/views/manager/information/Information') },
  { path: 'orders', name: 'Orders', meta: { name: '课程订单' }, component: () => import('@/views/manager/order/Orders') },
  { path: 'scoreOrder', name: 'ScoreOrder', meta: { name: '积分兑课' }, component: () => import('@/views/manager/score/ScoreOrder') },
  { path: 'fileOrder', name: 'FileOrder', meta: { name: '资料下载' }, component: () => import('@/views/manager/order/FileOrder') },
  { path: 'record', name: 'Record', meta: { name: '充值记录' }, component: () => import('@/views/manager/record/Record') },
  { path: 'userCluster', name: 'UserCluster', meta: { name: '用户聚类分析' }, component: () => import('@/views/manager/analysis/UserCluster') },
  { path: 'sentiment', name: 'SentimentAnalysis', meta: { name: '评论情感分析' }, component: () => import('@/views/manager/analysis/SentimentAnalysis') },
]
