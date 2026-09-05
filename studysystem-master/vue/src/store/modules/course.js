import { courseApi, scoreApi, infoApi } from '@/api'

const state = {
  recommendCourses: [],
  featuredCourses: [],
  courseList: [],
  courseDetail: null,
  scoreCourses: [],
  informationList: [],
  loading: false
}

const mutations = {
  SET_RECOMMEND_COURSES(state, courses) {
    state.recommendCourses = courses
  },
  SET_FEATURED_COURSES(state, courses) {
    state.featuredCourses = courses
  },
  SET_COURSE_LIST(state, courses) {
    state.courseList = courses
  },
  SET_COURSE_DETAIL(state, course) {
    state.courseDetail = course
  },
  SET_SCORE_COURSES(state, courses) {
    state.scoreCourses = courses
  },
  SET_INFORMATION_LIST(state, information) {
    state.informationList = information
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  }
}

const actions = {
  // 获取推荐课程
  async getRecommendCourses({ commit }) {
    commit('SET_LOADING', true)
    try {
      const res = await courseApi.getSmartRecommend(8)
      if (res.code === '200') {
        const courses = res.data && res.data.courses ? res.data.courses : res.data
        commit('SET_RECOMMEND_COURSES', courses || [])
      }
    } catch (error) {
      console.error('获取推荐课程失败:', error)
      // 尝试使用备用接口
      try {
        const res = await courseApi.getRecommendCourses(8)
        if (res.code === '200') {
          commit('SET_RECOMMEND_COURSES', res.data || [])
        }
      } catch (e) {
        console.error('获取推荐课程备用接口失败:', e)
      }
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 获取精选课程
  async getFeaturedCourses({ commit }, type) {
    commit('SET_LOADING', true)
    try {
      if (type === 'SCORE') {
        const recommendRes = await scoreApi.getRecommend()
        if (recommendRes.code === '200') {
          commit('SET_FEATURED_COURSES', [recommendRes.data])
        }
        const topRes = await scoreApi.getTop8()
        if (topRes.code === '200') {
          commit('SET_SCORE_COURSES', topRes.data || [])
        }
      } else {
        const recommendRes = await courseApi.getRecommend(type)
        if (recommendRes.code === '200') {
          commit('SET_FEATURED_COURSES', [recommendRes.data])
        }
        const topRes = await courseApi.getTop8(type)
        if (topRes.code === '200') {
          commit('SET_COURSE_LIST', topRes.data || [])
        }
      }
    } catch (error) {
      console.error('获取精选课程失败:', error)
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 获取学习资料
  async getInformationList({ commit }) {
    commit('SET_LOADING', true)
    try {
      const res = await infoApi.getTop8()
      if (res.code === '200') {
        commit('SET_INFORMATION_LIST', res.data || [])
      }
    } catch (error) {
      console.error('获取学习资料失败:', error)
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 获取课程详情
  async getCourseDetail({ commit }, id) {
    commit('SET_LOADING', true)
    try {
      const res = await courseApi.getDetail(id)
      if (res.code === '200') {
        commit('SET_COURSE_DETAIL', res.data)
      }
      return res
    } catch (error) {
      console.error('获取课程详情失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  recommendCourses: state => state.recommendCourses,
  featuredCourses: state => state.featuredCourses,
  courseList: state => state.courseList,
  courseDetail: state => state.courseDetail,
  scoreCourses: state => state.scoreCourses,
  informationList: state => state.informationList,
  loading: state => state.loading
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}