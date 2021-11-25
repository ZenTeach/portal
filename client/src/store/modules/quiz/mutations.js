export default {
  ADD_TO_SELECTED_QUIZ_QUESTION (state, payload) {
    state.quiz_questions.append(payload)
  },

  REMOVE_SELECTED_QUIZ_QUESTION (state, payload) {
    const quizId = state.quiz_questions.findIndex(x => x.q_id === payload.q_id)
    state.quiz_questions.slice(quizId, 1)
  },

  TOGGLE_QUIZ_QUESTIONS (state, payload) {
    state.quiz_questions = payload
  },

  SET_QUIZ_SESSION (state) {
    state.has_started = true
  },

  UNSET_QUIZ_SESSION (state) {
    state.has_started = false
  },

  SET_QUIZ_SUBMISSION (state) {
    state.has_submitted = true
  },

  SET_ERROR (state, payload) {
    state.error = payload
  },

  RESET_ERROR (state) {
    state.error = null
  },

  SET_ERROR_STATE (state, payload) {
    state.has_error = payload
  },

  SET_LOADING (state, payload) {
    state.loading = payload
  },

  SET_STARTED (state, payload) {
    state.has_started = payload
  },

  SET_QUIZ_NAME (state, name) {
    state.name = name
  },

  UNSET_QUIZ_SUBMISSION (state) {
    state.has_submitted = false
  },

  SET_QUIZ_SUBJECT (state, payload) {
    state.subject = payload
  },

  SET_QUIZ_UUID (state, payload) {
    state.uuid = payload
  },

  UNSET_QUIZ_SUBJECT (state) {
    state.subject = ''
  },

  UNSET_QUIZ_UUID (state) {
    state.uuid = ''
  },

  SET_REPORTCARD (state, payload) {
    state.report_card = payload
  },

  UNSET_REPORTCARD (state) {
    state.report_card = []
  },

  SET_GRADEDQUIZZES (state, payload) {
    state.graded_quizzes = payload
  },

  UNSET_GRADEDQUIZZES (state) {
    state.graded_quizzes = []
  }
}
