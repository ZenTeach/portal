import { fetchQuestions } from '../../../service/questions'

export default {
  QUERY_QUESTIONS ({ commit }, payload) {
    fetchQuestions(payload)
      .then(result => {
        const {
          data: questions
        } = result
        commit('UPDATE_QUESTION_SEARCH', questions)
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
      })
  },

  TOGGLE_ERROR ({ commit }, payload = {}) {
    commit('TOGGLE_ERROR', payload)
  }
}
