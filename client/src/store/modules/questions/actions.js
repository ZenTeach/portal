import {
  getUserQuestions,
  userCreatedQuestion
} from '../../../service/question_service'

const GETQUESTIONS = ({ commit, dispatch }) => {
  getUserQuestions()
    .then(
      data => {
        commit('QUESTIONLIST_UPDATED', data.questions)
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      })
}

const CREATEQUESTION = ({ commit, dispatch }, payload) => {
  userCreatedQuestion(payload)
    .then(
      _data => {
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        dispatch('app/TOGGLE_ERROR', { message: 'Question created successfully!' }, { root: true })
        dispatch('GETQUESTIONS')
      },
      error => {
        commit('app/TOGGLE_ERROR', data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      }
    )
}

export default {
  GETQUESTIONS,
  CREATEQUESTION
}
