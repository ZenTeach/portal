import {
  submitQuiz,
  startQuiz,
  updateQuiz, fetchQuiz,
  fetchReportCard,
  sendReportCard,
  fetchGradedReportCards
} from '@/service/quiz_service'

export default {
  START_QUIZ ({ commit, dispatch }, payload) {
    const { studentEmail, quizUUID } = payload
    // set a loading state
    commit('RESET_ERROR')
    commit('UNSET_QUIZ_SESSION')
    commit('SET_ERROR_STATE', false)
    commit('SET_LOADING', true)
    startQuiz(studentEmail, quizUUID).then(
      data => {
        commit('SET_ERROR_STATE', false)
        commit('SET_QUIZ_SESSION')
        commit('SET_LOADING', false)
        dispatch('LOAD_QUIZ', quizUUID)
      },
      error => {
        commit('SET_ERROR', error.response.data)
        commit('SET_ERROR_STATE', true)
        commit('SET_LOADING', false)
      }
    )
  },

  LOAD_QUIZ ({ commit, dispatch }, payload) {
    commit('SET_LOADING', true)
    fetchQuiz(payload).then(
      data => {
        const { uuid, questions, subject, name } = data.data
        commit('SET_QUIZ_SUBJECT', subject)
        commit('SET_QUIZ_UUID', uuid)
        commit('TOGGLE_QUIZ_QUESTIONS', questions)
        commit('SET_QUIZ_NAME', name)
        commit('TOGGLE_QUIZ_PRIVATE', data.data.private)
        commit('SET_LOADING', false)
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
        commit('SET_LOADING', false)
      }
    )
  },

  UPDATE_QUIZ ({ commit, dispatch }, payload) {
    const { quizUUID, ...updateParams } = payload
    console.log(quizUUID, updateParams)
    updateQuiz(quizUUID, updateParams).then(
      data => {
        commit('app/TOGGLE_ERROR', 'Class quiz was updated successfully.', { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        dispatch('LOAD_QUIZ', quizUUID)
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      }
    )
  },

  FETCH_REPORTCARD ({ commit, dispatch }, gradeId) {
    fetchReportCard(gradeId).then(
      data => {
        commit('UNSET_REPORTCARD')
        commit('app/TOGGLE_APP_LOADING', true, { root: true })
        commit('SET_REPORTCARD', data)
        commit('app/TOGGLE_APP_LOADING', false, { root: true })
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      }
    )
  },

  SUBMIT_QUIZ ({ commit, dispatch }, payload) {
    commit('SET_LOADING', true)
    submitQuiz(payload).then(
      data => {
        commit('UNSET_QUIZ_SESSION')
        commit('SET_QUIZ_SUBMISSION')
        commit('UNSET_QUIZ_UUID')
        commit('UNSET_QUIZ_SUBJECT')
        commit('TOGGLE_QUIZ_QUESTIONS', {})
        commit('SET_LOADING', false)
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        dispatch('app/TOGGLE_ERROR', { message: 'Quiz submitted!' }, { root: true })
      },
      error => {
        commit('SET_LOADING', false)
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      }
    )
  },

  SENDSTUDENTREPORTCARD ({ commit, dispatch }, quizUUID) {
    sendReportCard(quizUUID)
      .then(data => {
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        dispatch('app/TOGGLE_ERROR', { message: data.message }, { root: true })
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      })
  },

  FETCH_GRADEDQUIZZES ({ commit, dispatch }, classQuizId) {
    fetchGradedReportCards(classQuizId).then(
      data => {
        const graded = data.reduce((accumulator, x) => {
          accumulator.push({
            gradeId: x.uuid,
            email: x.student.email,
            score: x.score
          })
          return accumulator
        }, [])

        commit('UNSET_GRADEDQUIZZES')
        commit('app/TOGGLE_APP_LOADING', true, { root: true })
        commit('SET_GRADEDQUIZZES', graded)
        commit('app/TOGGLE_APP_LOADING', false, { root: true })
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      }
    )
  }
}
