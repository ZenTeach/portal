import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function searchKnowledgeItems (payload) {
  return Api.post('/knowledge_item/search', payload)
    .then(handleResponse)
    .then(data => data)
}

export function createKnowledgeItem (payload) {
  return Api.post('/knowledge_items', payload)
    .then(handleResponse)
    .then(data => data)
}
