import {
  fetchQuestions,
  fetchKis,
  fetchTopics,
  fetchQuestionsFromTopicsAndKIs
} from '../../../service/questions'

export default {
  QUERY_QUESTIONS ({ commit, dispatch }, payload) {
    fetchQuestions(payload)
      .then(result => {
        const { data: questions } = result
        commit('UPDATE_QUESTION_SEARCH', questions)
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error')
      })
  },

  FETCH_KIS ({ commit, dispatch }, topics) {
    fetchKis(topics)
      .then(result => {
        commit('app/UPDATE_KIS', result, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error')
      })
  },
  FETCH_TOPICS ({ commit, dispatch }, subject) {
    fetchTopics(subject)
      .then(result => {
        commit('app/UPDATE_TOPICS', result, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error')
      })
  },
  TOGGLE_ERROR ({ commit }, payload = {}) {
    commit('TOGGLE_ERROR', payload)
  },
  TOGGLE_APP_STATUS ({ commit }, payload = '') {
    commit('TOGGLE_APP_STATUS', payload)
  },
  FETCH_QUESTIONS_FASTTRACKED ({ commit, dispatch }, topics, kis) {
    fetchQuestionsFromTopicsAndKIs(topics, kis)
      .then(data => {
        const questions = data.data
        commit('UPDATE_QUESTION_SEARCH', questions)
        questions.forEach(question => commit('ADD_SELECTED_QUESTIONS', question))
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        dispatch('app/TOGGLE_APP_STATUS', 'error')
      })
  }
}
