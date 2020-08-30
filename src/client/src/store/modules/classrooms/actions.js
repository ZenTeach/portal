import {
  fetchClasses,
  addNewClass,
  fetchCurrentClass,
  inviteStudent,
  deleteClassroom,
  removeStudent
} from '../../../service/classrooms'

const GETCLASSES = ({ commit }) => {
  fetchClasses()
    .then(
      data => {
        commit('CLASSLIST_UPDATED', data.data)
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      })
}

const INVITE_STUDENT = ({ commit, dispatch }, payload) => {
  const { classId, ...studentData } = payload
  inviteStudent(classId, studentData)
    .then(_data => {
      dispatch('GETCURRENTCLASS', classId)
    },
    error => {
      commit('app/TOGGLE_ERROR', error.response.data, { root: true })
    })
}

const CREATECLASS = ({ commit, dispatch }, payload) => {
  addNewClass(payload)
    .then(
      _data => {
        commit('CLASSLIST_ADDED', payload)
        dispatch('GETCLASSES')
      },
      error => {
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

const DELETECLASSROOM = ({ commit, dispatch }, classId) => {
  deleteClassroom(classId)
    .then(
      _data => {
        dispatch('GETCLASSES')
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      })
}

const REMOVESTUDENTFROMCLASS = ({ commit, dispatch }, payload) => {
  const { classId, studentId } = payload
  console.log('classId, ', classId, ' studentId, ', studentId)
  removeStudent(classId, studentId)
    .then(
      _data => {
        dispatch('GETCURRENTCLASS', classId)
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
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
