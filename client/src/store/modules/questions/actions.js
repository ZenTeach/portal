import {
  getUserQuestions
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

export default {
  GETQUESTIONS
}
