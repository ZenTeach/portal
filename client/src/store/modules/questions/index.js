import actions from './actions'
import getters from './getters'
import mutations from './mutations'

const state = {
  questions: [],
  current_question: {}
}

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations
}
