import { submitQuiz, startQuiz, fetchQuiz } from '@/service/quiz_service'

export default {
  START_QUIZ ({ commit }, payload) {
    const { studentEmail, quizUUID } = payload
    startQuiz(studentEmail, quizUUID).then(
      data => {
        commit('SET_QUIZ_SESSION')
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      }
    )
  },

  LOAD_QUIZ ({ commit }, payload) {
    fetchQuiz(payload).then(
      data => {
        const { uuid, questions, subject } = data.data
        commit('SET_QUIZ_SUBJECT', subject)
        commit('SET_QUIZ_UUID', uuid)
        commit('TOGGLE_QUIZ_QUESTIONS', questions)
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      }
    )
  },
  SUBMIT_QUIZ ({ commit }, payload) {
    submitQuiz(payload).then(
      data => {
        commit('UNSET_QUIZ_SESSION')
        commit('SET_QUIZ_SUBMISSION')
        commit('UNSET_QUIZ_UUID')
        commit('UNSET_QUIZ_SUBJECT')
        commit('TOGGLE_QUIZ_QUESTIONS', {})
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      }
    )
  }
}
