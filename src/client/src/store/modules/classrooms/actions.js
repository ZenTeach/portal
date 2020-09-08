import {
  fetchClasses,
  addNewClass,
  fetchCurrentClass,
  inviteStudent,
  deleteClassroom,
  removeStudent
} from '../../../service/classrooms'

const GETCLASSES = ({ commit, dispatch }) => {
  fetchClasses()
    .then(
      data => {
        commit('CLASSLIST_UPDATED', data.data)
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      })
}

const INVITE_STUDENT = ({ commit, dispatch }, payload) => {
  const { classId, ...studentData } = payload
  const inviteMessage = { message: 'Invite sent!' }
  inviteStudent(classId, studentData)
    .then(_data => {
      dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
      dispatch('app/TOGGLE_ERROR', inviteMessage, { root: true })
      dispatch('GETCURRENTCLASS', classId)
    },
    error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
    })
}

const CREATECLASS = ({ commit, dispatch }, payload) => {
  addNewClass(payload)
    .then(
      _data => {
        commit('CLASSLIST_ADDED', payload)
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        dispatch('app/TOGGLE_ERROR', { message: 'Class created successfully!' }, { root: true })
        dispatch('GETCLASSES')
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      })
}

const GETCURRENTCLASS = ({ commit, dispatch }, payload) => {
  fetchCurrentClass(payload)
    .then(response => {
      if (response.status === 'success') {
        commit('UPDATE_CURRENT_CLASS', response.data)
      }
    })
    .catch(error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
    })
}

const DELETECLASSROOM = ({ commit, dispatch }, classId) => {
  deleteClassroom(classId)
    .then(
      _data => {
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        dispatch('app/TOGGLE_ERROR', { message: 'Classroom deleted successfully' }, { root: true })
        dispatch('GETCLASSES')
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      })
}

const REMOVESTUDENTFROMCLASS = ({ commit, dispatch }, payload) => {
  const { classId, studentId } = payload
  removeStudent(classId, studentId)
    .then(
      _data => {
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        dispatch('app/TOGGLE_ERROR', { message: 'Student removed!' }, { root: true })
        dispatch('GETCURRENTCLASS', classId)
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      })
}

export default {
  GETCLASSES,
  CREATECLASS,
  GETCURRENTCLASS,
  DELETECLASSROOM,
  INVITE_STUDENT,
  REMOVESTUDENTFROMCLASS
}
