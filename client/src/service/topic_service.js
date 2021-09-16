import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function searchTopic (topicSearchString) {
  return Api.post(
    '/topics/search',
    topicSearchString)
    .then(handleResponse)
    .then(data => data)
}

export function createTopic (createTopicPayload) {
  return Api.post(
    '/topics',
    createTopicPayload)
    .then(handleResponse)
    .then(data => data)
}
