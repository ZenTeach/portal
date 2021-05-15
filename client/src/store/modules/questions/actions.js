import {
  getUserQuestions,
  userCreatedQuestion,
  deleteUserCreatedQuestion,
  updateUserCreatedQuestion
} from '../../../service/question_service'
import router from '@/router'

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
        router.push('/questions')
      },
      error => {
        const errorMessage = error.response.data
        commit('app/TOGGLE_ERROR', errorMessage, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      }
    )
}

const DELETEQUESTION = ({ commit, dispatch }, questionId) => {
  deleteUserCreatedQuestion(questionId)
    .then(
      data => {
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        dispatch('app/TOGGLE_ERROR', data, { root: true })
        dispatch('GETQUESTIONS')
      },
      error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      }
    )
}

const UPDATEQUESTION = ({ commit, dispatch }, data) => {
  const { questionId, payload } = data
  updateUserCreatedQuestion(questionId, payload)
    .then(
      data => {
        dispatch('app/TOGGLE_APP_STATUS', 'success', { root: true })
        dispatch('app/TOGGLE_ERROR', data, { root: true })
        dispatch('GETQUESTIONS')
        commit('UNSET_CURRENTQUESTION')
        router.push('/questions')
      },
      error => {
        dispatch('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error', { root: true })
      }
    )
}

export default {
  GETQUESTIONS,
  CREATEQUESTION,
  DELETEQUESTION,
  UPDATEQUESTION
}
