import {
  fetchClasses,
  addNewClass,
  fetchCurrentClass,
  inviteStudent
} from '../../../service/classrooms'

const GETCLASSES = ({ commit }) => {
  fetchClasses()
    .then(response => {
      if (response.status === 'success') {
        commit('CLASSLIST_UPDATED', response.data)
      }
    })
    .catch(error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    })
}

const INVITE_STUDENT = ({ commit }, payload) => {
  console.log(payload)
  const { classId, ...studentData } = payload
  console.log(classId, studentData)
  inviteStudent(classId, studentData)
    .then(data => {
      console.log(data)
    },
    error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    })
}
const CREATECLASS = ({ commit }, payload) => {
  addNewClass(payload)
    .then(response => {
      if (response.status === 'success') {
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
      if (response.status === 'success') {
        commit('UPDATE_CURRENT_CLASS', response.data)
      }
    })
    .catch(error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    })
}

export default {
  GETCLASSES,
  CREATECLASS,
  GETCURRENTCLASS,
  INVITE_STUDENT,
  IMPORTSTUDENTSFROMCSV
}
