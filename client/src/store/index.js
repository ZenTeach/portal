import Vue from 'vue'
import Vuex from 'vuex'
import VuexPersistence from 'vuex-persist'
import app from '@/store/modules/app'
import user from '@/store/modules/user'
import classrooms from '@/store/modules/classrooms'
import quiz from '@/store/modules/quiz'
import questions from '@/store/modules/questions'

Vue.use(Vuex)

const vuexLocalStore = new VuexPersistence({
  storage: window.sessionStorage
})

const store = new Vuex.Store({
  modules: {
    app: app,
    user: user,
    classrooms: classrooms,
    quiz: quiz,
    questions: questions
  },
  state: {
    // global state
  },
  mutations: {},
  actions: {},
  getters: {},
  plugins: [vuexLocalStore.plugin]
})

export default store
