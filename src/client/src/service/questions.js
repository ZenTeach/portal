import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function fetchQuestions (searchPayload) {
  return Api.post('/question/search', searchPayload)
    .then(handleResponse)
    .then(data => data)
}
