import Vue from 'vue'
import Vuex from 'vuex'
import VuexPersistence from 'vuex-persist'
import app from '@/store/modules/app'
import user from '@/store/modules/user'
import classrooms from '@/store/modules/classrooms'
import quiz from '@/store/modules/quiz'
import questions from '@/store/modules/questions'
import settings from '@/store/modules/settings'

Vue.use(Vuex)

const vuexLocalSessionStore = new VuexPersistence({
  storage: window.sessionStorage,
  modules: ['app', 'user', 'questions', 'classrooms']
})

const vuexLocalStorageStore = new VuexPersistence({
  storage: window.localStorage,
  modules: ['settings']
})

const store = new Vuex.Store({
  modules: {
    app: app,
    user: user,
    classrooms: classrooms,
    quiz: quiz,
    settings: settings,
    questions: questions
  },
  state: {
    // global state
  },
  mutations: {},
  actions: {},
  getters: {},
  plugins: [vuexLocalSessionStore.plugin, vuexLocalStorageStore.plugin]
})

export default store
