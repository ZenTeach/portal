import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function confirmStudentAccount (token) {
  return Api.post('/student/confirm', {
    token: token
  })
    .then(handleResponse)
    .then(data => data)
}

export function sendStudentConfirmationEmail (studentId) {
  return Api.get(`/student/${studentId}/send_confirmation`)
    .then(handleResponse)
    .then(data => data)
}

export function loginUser (payload) {
  return Api.post('/student/login', payload)
    .then(handleResponse)
    .then(data => data)
}
