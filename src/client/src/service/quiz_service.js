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
