import actions from './actions'
import getters from './getters'
import mutations from './mutations'

const state = {
  loggedIn: false,
  loading: false,
  drawer: true,
  drawerMinified: false,
  inviteModalVisible: false,
  error: {},
  status: '',
  // stores subjects in the form of
  // [{id: x, name: Chemistry, enabled: True, remarks: ''}]
  subjects: [],
  questionSearch: [],
  knowledgeItems: {},
  topics: [],
  questionList: []
}

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations
}
