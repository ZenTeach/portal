import actions from './actions'
import getters from './getters'
import mutations from './mutations'

const state = {
  quiz_questions: [],
  subject: '',
  uuid: '',
  has_started: false,
  has_submitted: false
}

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations
}
