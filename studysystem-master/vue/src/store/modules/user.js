import { userApi } from '@/api'

const state = {
  userInfo: JSON.parse(localStorage.getItem('xm-user') || '{}'),
  isLoggedIn: !!localStorage.getItem('xm-user'),
  loading: false
}

const mutations = {
  SET_USER_INFO(state, userInfo) {
    state.userInfo = userInfo
    state.isLoggedIn = true
    localStorage.setItem('xm-user', JSON.stringify(userInfo))
  },
  CLEAR_USER_INFO(state) {
    state.userInfo = {}
    state.isLoggedIn = false
    localStorage.removeItem('xm-user')
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  }
}

const actions = {
  // 登录
  async login({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const res = await userApi.login(data)
      if (res.code === '200') {
        commit('SET_USER_INFO', res.data)
        return res
      }
      return res
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 注册
  async register({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const res = await userApi.register(data)
      return res
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 获取用户信息
  async getUserInfo({ commit, state }) {
    if (!state.userInfo.id) return
    
    commit('SET_LOADING', true)
    try {
      const res = await userApi.getInfo(state.userInfo.id)
      if (res.code === '200') {
        commit('SET_USER_INFO', res.data)
      }
      return res
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
  
  // 退出登录
  logout({ commit }) {
    commit('CLEAR_USER_INFO')
  },
  
  // 更新用户信息
  async updateUserInfo({ commit }, data) {
    commit('SET_LOADING', true)
    try {
      const res = await userApi.update(data)
      if (res.code === '200') {
        commit('SET_USER_INFO', res.data)
      }
      return res
    } catch (error) {
      console.error('更新用户信息失败:', error)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  }
}

const getters = {
  userInfo: state => state.userInfo,
  isLoggedIn: state => state.isLoggedIn,
  loading: state => state.loading,
  userId: state => state.userInfo.id,
  username: state => state.userInfo.username,
  role: state => state.userInfo.role
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}