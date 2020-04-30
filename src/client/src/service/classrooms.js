import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function fetchClasses () {
  return Api.get('/school_class/owned')
    .then(handleResponse)
    .then(data => data)
}

export function addNewClass (payload) {
  return Api.post('/school_class', payload)
    .then(handleResponse)
    .then(data => data)
}

export function fetchCurrentClass (classId) {
  return Api.get(`/school_class/${classId}`)
    .then(handleResponse)
    .then(data => data)
}

export function fetchQuizPDF (quizId) {
  return Api.get(`/class_quiz/pdf_view/${quizId}`, { responseType: 'blob' })
    .then(handleResponse)
    .then(data => data)
}

export function inviteStudent (classId, payload) {
  console.log('inviteStudent', classId, payload)
  return Api.post(`/school_class/${classId}/student/invite`, payload)
    .then(handleResponse)
    .then(data => data)
}
