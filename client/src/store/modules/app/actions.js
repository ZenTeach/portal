import {
  fetchQuestions,
  fetchKis,
  fetchTopics,
  fetchQuestionsFromTopicsAndKIs
} from '../../../service/question_service'

import { searchTopic, createTopic } from '../../../service/topic_service'
import { searchKnowledgeItems, createKnowledgeItem } from '../../../service/knowledge_item_service'

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
            question.isSelected = false
          })
          commit('UPDATE_QUESTION_SEARCH', questions)
        }
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
        commit('app/RESET_KIS', {}, { root: true })
        commit('app/UPDATE_TOPICS', result, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data, { root: true })
        commit('TOGGLE_APP_STATUS', 'error')
      })
  },
  SEARCH_TOPICS ({ commit }, payload) {
    searchTopic(payload)
      .then(result => {
        const topics = result.data.map(topic => topic.value)

        if (topics.length === 0) {
          console.info('no topics found')
        }

        commit('app/RESET_KIS', {}, { root: true })
        commit('app/UPDATE_TOPICS', topics, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data || error, { root: true })
        commit('TOGGLE_APP_STATUS', 'error')
        throw error
      })
  },
  CREATE_TOPIC ({ commit }, payload) {
    createTopic(payload)
      .then(result => {
        const newTopic = result.data.value

        commit('app/RESET_KIS', {}, { root: true })
        commit('app/ADD_TOPIC', newTopic, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data || error, { root: true })
        commit('TOGGLE_APP_STATUS', 'error')
        throw error
      })
  },
  SEARCH_KNOWLEDGE_ITEMS ({ commit }, payload) {
    searchKnowledgeItems(payload)
      .then(result => {
        const KIs = result.data.map(ki => [ki.topic.value, ki.value])
        commit('app/UPDATE_KIS', KIs, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data || error, { root: true })
        commit('TOGGLE_APP_STATUS', 'error')
        throw error
      })
  },
  CREATE_KNOWLEDGE_ITEM ({ commit }, payload) {
    createKnowledgeItem(payload)
      .then(result => {
        const newKiItem = [[result.data.topic.value, result.data.value]]
        commit('app/UPDATE_KIS', newKiItem, { root: true })
      })
      .catch(error => {
        commit('app/TOGGLE_ERROR', error.response.data || error, { root: true })
        commit('TOGGLE_APP_STATUS', 'error')
        throw error
      })
  },

  TOGGLE_ERROR ({ commit }, payload = {}) {
    commit('TOGGLE_ERROR', payload)
  },
  TOGGLE_APP_STATUS ({ commit }, payload = '') {
    commit('TOGGLE_APP_STATUS', payload)
  },
  FETCH_QUESTIONS_FASTTRACKED ({ commit }, payload) {
    const { topics, kis } = payload
    fetchQuestionsFromTopicsAndKIs(topics, kis)
      .then(data => {
        const questions = data.data
        commit('UPDATE_QUESTION_SEARCH', questions)
        questions.forEach(question => {
          question.isSelected = true
          commit('ADD_SELECTED_QUESTIONS', question)
        }
        )
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
