import actions from './actions'
import getters from './getters'
import mutations from './mutations'

const state = {
  loggedIn: false,
  loading: false,
  drawer: true,
  drawerMinified: false,
  error: {},
  questionSearch: [],
  knowledgeItems: [],
  questionList: []
}

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations
}
