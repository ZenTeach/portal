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
  return Api.post(`/school_class/${classId}/student`, payload)
    .then(handleResponse)
    .then(data => data)
}

export function deleteClassroom (classId) {
  return Api.remove(`/school_class/${classId}`)
    .then(handleResponse)
    .then(data => data)
}

export function removeStudent (classId, studentId) {
  return Api.remove(`/school_class/${classId}/student?student_id=${studentId}`)
    .then(handleResponse)
    .then(data => data)
}

export function updateStudentEmail (classId, payload) {
  return Api.patch(`/school_class/${classId}/student`, payload)
    .then(handleResponse)
    .then(data => data)
}

export function updateClassRoom (classId, payload) {
  return Api.put(`/school_class/${classId}`, payload)
    .then(handleResponse)
    .then(data => data)
}
