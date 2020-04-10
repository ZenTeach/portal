import {
  fetchClasses,
  addNewClass,
  fetchCurrentClass
} from '../../../service/classrooms'

const GETCLASSES = ({ commit }) => {
  fetchClasses()
    .then(response => {
      if (response.status === 200) {
        commit('CLASSLIST_UPDATED', response.data.data)
      }
    })
    .catch(error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    })
}

const CREATECLASS = ({ commit }, payload) => {
  addNewClass(payload)
    .then(response => {
      if (response.status === 200) {
        commit('CLASSLIST_ADDED', payload)
      }
    })
    .catch(error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    })
}

const GETCURRENTCLASS = ({ commit }, payload) => {
  fetchCurrentClass(payload)
    .then(response => {
      if (response.status === 200) {
        commit('UPDATE_CURRENT_CLASS', response.data.data)
      }
    })
    .catch(error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    })
}

export default {
  GETCLASSES,
  CREATECLASS,
  GETCURRENTCLASS
}
