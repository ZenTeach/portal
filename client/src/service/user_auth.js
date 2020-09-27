import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function loginUser (payload) {
  return Api.post('/teacher/login', payload)
    .then(handleResponse)
    .then(data => data)
}

export function logoutUser () {
  return Api.post('/teacher/logout')
    .then(handleResponse)
    .then(data => data)
}

export function registerUser (payload) {
  return Api.post('/teacher/registration', payload)
    .then(handleResponse)
    .then(data => data)
}

export function getCurrentUser () {
  return Api.get('/teacher/current')
    .then(handleResponse)
    .then(data => data)
}

export function sendAccountRecovery (email) {
  return Api.get(`/teacher/reset-password?email=${email}`)
    .then(handleResponse)
    .then(data => data)
}

export function changePassword (payload) {
  return Api.post('/teacher/reset-password', payload)
    .then(handleResponse)
    .then(data => data)
}

export function confirmAccount (token) {
  return Api.post('/teacher/confirm', {
    token: token
  }).then(handleResponse).then(data => data)
}

export function userInvite (email) {
  return Api.post('/teacher/invite', {
    email: email
  }).then(handleResponse).then(data => data)
}
