import { fetchQuestions, fetchKis, fetchTopics } from '../../../service/questions'

export default {
  QUERY_QUESTIONS ({ commit }, payload) {
    fetchQuestions(payload)
      .then(result => {
        const { data: questions } = result
        commit('UPDATE_QUESTION_SEARCH', questions)
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      })
  },

  FETCH_KIS ({ commit }, topic) {
    fetchKis(topic)
      .then(result => {
        commit('app/UPDATE_KIS', result, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      })
  },
  FETCH_TOPICS ({ commit }, subject) {
    fetchTopics(subject)
      .then(result => {
        commit('app/UPDATE_TOPICS', result, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      })
  },
  TOGGLE_ERROR ({ commit }, payload = {}) {
    commit('TOGGLE_ERROR', payload)
  }
}
