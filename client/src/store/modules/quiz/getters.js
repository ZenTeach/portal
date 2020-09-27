export default {
  quizQuestions (state) {
    return state.quiz_questions
  },

  subject (state) {
    return state.subject
  },

  uuid (state) {
    return state.uuid
  },

  hasSubmitted (state) {
    return state.has_submitted
  },

  reportCard (state) {
    return state.report_card
  },

  gradedQuizzes (state) {
    return state.graded_quizzes
  }
}
