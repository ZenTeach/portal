import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function confirmStudentAccount (token) {
  return Api.post('/teacher/confirm', {
    token: token
  }).then(handleResponse).then(data => data)
}
