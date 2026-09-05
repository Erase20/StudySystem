import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'
import course from './modules/course'
import common from './modules/common'

Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    user,
    course,
    common
  }
})

export default store