import {
  fetchQuestions,
  fetchKis,
  fetchTopics,
  fetchQuestionsFromTopicsAndKIs
} from '../../../service/question_service'

export default {
  QUERY_QUESTIONS ({ commit }, payload) {
    fetchQuestions(payload)
      .then(result => {
        const { data: questions } = result
        commit('UPDATE_QUESTION_SEARCH', questions)
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        commit('TOGGLE_APP_STATUS', 'error')
      })
  },

  FETCH_KIS ({ commit }, topics) {
    fetchKis(topics)
      .then(result => {
        commit('app/UPDATE_KIS', result, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        commit('TOGGLE_APP_STATUS', 'error')
      })
  },
  FETCH_TOPICS ({ commit }, subject) {
    fetchTopics(subject)
      .then(result => {
        commit('app/UPDATE_TOPICS', result, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        commit('TOGGLE_APP_STATUS', 'error')
      })
  },
  TOGGLE_ERROR ({ commit }, payload = {}) {
    commit('TOGGLE_ERROR', payload)
  },
  TOGGLE_APP_STATUS ({ commit }, payload = '') {
    commit('TOGGLE_APP_STATUS', payload)
  },
  FETCH_QUESTIONS_FASTTRACKED ({ commit }, topics, kis) {
    fetchQuestionsFromTopicsAndKIs(topics, kis)
      .then(data => {
        const questions = data.data
        commit('UPDATE_QUESTION_SEARCH', questions)
        questions.forEach(question => commit('ADD_SELECTED_QUESTIONS', question))
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        commit('TOGGLE_APP_STATUS', 'error')
      })
  }
}
