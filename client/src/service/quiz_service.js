import Api from '@/service/Api'
import { handleResponse } from '@/service/service_utils'

export function fetchQuiz (quizId) {
  return Api.get('/class_quiz/' + quizId)
    .then(handleResponse)
    .then(data => data)
}

export function startQuiz (studentEmail, quizUUID) {
  return Api.get('/submit_quiz', {
    params: {
      email: studentEmail,
      quiz: quizUUID
    }
  })
    .then(handleResponse)
    .then(data => data)
}

export function submitQuiz (payload) {
  return Api.post('/submit_quiz', payload)
    .then(handleResponse)
    .then(data => data)
}

export function updateQuiz (quizUUID, payload) {
  return Api.patch(`/class_quiz/${quizUUID}`, payload)
    .then(handleResponse)
    .then(data => data)
}

export function fetchReportCard (gradeId) {
  return Api.get(`/class_quiz/report_card/${gradeId}`)
    .then(handleResponse)
    .then(data => data)
}

export function fetchGradedReportCards (classQuizId) {
  return Api.get(`class_quiz/${classQuizId}/graded`)
    .then(handleResponse)
    .then(data => data)
}

export function sendReportCard (gradeUUID) {
  return Api.get(`class_quiz/${gradeUUID}/send_report`)
    .then(handleResponse)
    .then(data => data)
}
