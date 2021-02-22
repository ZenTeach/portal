import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function confirmStudentAccount (token) {
  return Api.post('/student/confirm', {
    token: token
  }).then(handleResponse).then(data => data)
}
