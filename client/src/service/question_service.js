import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function fetchQuestions (searchPayload) {
  return Api.post('/question/search', searchPayload)
    .then(handleResponse)
    .then(data => data)
}

export function fetchKis (topics) {
  return Api.post('/question/filter/ki', topics)
    .then(handleResponse)
    .then(data => data)
}

export function fetchTopics (subject) {
  return Api.get(`/question/filter/topic/${subject}`)
    .then(handleResponse)
    .then(data => data)
}

export function fetchQuestionsFromTopicsAndKIs (topics, kis) {
  return Api.post('/question/fetch', {
    topics: topics,
    kis: kis
  })
    .then(handleResponse)
    .then(data => data)
}

export function getUserQuestions () {
  return Api.get('/question/user_created')
    .then(handleResponse)
    .then(data => data)
}

export function userCreatedQuestion (payload) {
  return Api.post('/question/user_created', payload)
    .then(handleResponse)
}
