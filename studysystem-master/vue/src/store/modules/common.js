const state = {
  loading: false,
  message: {
    show: false,
    type: 'info',
    content: ''
  }
}

const mutations = {
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_MESSAGE(state, message) {
    state.message = {
      show: true,
      ...message
    }
  },
  HIDE_MESSAGE(state) {
    state.message.show = false
  }
}

const actions = {
  // 显示消息
  showMessage({ commit }, message) {
    commit('SET_MESSAGE', message)
    // 3秒后自动隐藏
    setTimeout(() => {
      commit('HIDE_MESSAGE')
    }, 3000)
  },
  
  // 显示加载状态
  showLoading({ commit }) {
    commit('SET_LOADING', true)
  },
  
  // 隐藏加载状态
  hideLoading({ commit }) {
    commit('SET_LOADING', false)
  }
}

const getters = {
  loading: state => state.loading,
  message: state => state.message
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}