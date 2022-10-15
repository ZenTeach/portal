import actions from './actions'
import mutations from './mutations'
import getters from './getters'

const state = {
  current_user: {},
  loading: false
}

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
}
