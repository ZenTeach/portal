import {
  fetchQuestions,
  fetchKis,
  fetchTopics,
  fetchQuestionsFromTopicsAndKIs
} from '../../../service/question_service'

import {
  fetchSubjects
} from '../../../service/app_service'

import * as _ from 'lodash'

export default {
  QUERY_QUESTIONS ({ commit }, payload) {
    fetchQuestions(payload)
      .then(result => {
        if (_.has(result, 'data')) {
          let { data: questions } = result
          questions = _.each(questions, (question, i, a) => {
            // add flag for result lazy loading
            question.isActive = false
          })
          commit('UPDATE_QUESTION_SEARCH', questions)
        }
      })
      .catch(error => {
        console.error(error)
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
  },
  FETCH_SUBJECTS ({ commit }) {
    fetchSubjects()
      .then(subjects => {
        commit('UPDATE_SUBJECTS', subjects)
      })
      .catch(error => {
        commit('TOGGLE_ERROR', error.response.data)
      })
  }
}
