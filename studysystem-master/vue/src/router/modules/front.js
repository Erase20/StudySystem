/**
 * 前台用户路由配置
 */
export const frontRoutes = [
  { path: 'home', name: 'FrontHome', meta: { name: '系统首页' }, component: () => import('@/views/front/home/Home') },
  { path: 'course', name: 'Course', meta: { name: '全部课程' }, component: () => import('@/views/front/course/Course') },
  { path: 'courseDetail', name: 'CourseDetail', meta: { name: '课程详情' }, component: () => import('@/views/front/course/CourseDetail') },
  { path: 'scoreDetail', name: 'ScoreDetail', meta: { name: '积分课程详情' }, component: () => import('@/views/front/score/ScoreDetail') },
  { path: 'informationDetail', name: 'InformationDetail', meta: { name: '资源详情' }, component: () => import('@/views/front/information/InformationDetail') },
  { path: 'score', name: 'Score', meta: { name: '积分专区' }, component: () => import('@/views/front/score/Score') },
  { path: 'person', name: 'Person', meta: { name: '个人信息' }, component: () => import('@/views/front/user/Person') },
  { path: 'myInfo', name: 'MyInfo', meta: { name: '我的资料' }, component: () => import('@/views/front/user/MyInfo') },
  { path: 'information', name: 'Information', meta: { name: '海量资源' }, component: () => import('@/views/front/information/Information') },
  { path: 'orders', name: 'Orders', meta: { name: '已购课程' }, component: () => import('@/views/front/order/Orders') },
  { path: 'scoreOrder', name: 'ScoreOrder', meta: { name: '我的积分兑换' }, component: () => import('@/views/front/score/ScoreOrder') },
  { path: 'fileOrder', name: 'FileOrder', meta: { name: '历史下载' }, component: () => import('@/views/front/order/FileOrder') },
  { path: 'learningCenter', name: 'LearningCenter', meta: { name: '学习中心' }, component: () => import('@/views/front/learning/LearningCenter') },
  { path: 'analysis', name: 'DataAnalysis', meta: { name: '智能学习分析' }, component: () => import('@/views/front/analysis/DataAnalysis') },
]
