import { fetchAppSetting } from '@/service/settings_service'

const state = {
  examBoards: {}
}

const actions = {
  async fetchExamBoards ({ commit }) {
    try {
      const response = await fetchAppSetting()
      const { exam_board: examBoards } = response.appsettings
      commit('SET_EXAM_BOARDS', examBoards)
    } catch (error) {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      commit('TOGGLE_APP_STATUS', 'error')
    }
  }
}
const mutations = {
  SET_EXAM_BOARDS (state, examBoards) {
    state.examBoards = examBoards
  }
}
const getters = {
  getExamBoards: state => state.examBoards
}

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations
}
