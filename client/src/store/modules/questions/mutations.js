const QUESTIONLIST_UPDATED = (state, payload) => {
  state.questions = payload
}

const SET_CURRENTQUESTION = (state, payload) => {
  state.current_question = payload
}

const UNSET_CURRENTQUESTION = (state) => {
  state.current_question = {}
}

const RESET_QUESTIONS = (state) => {
  state.questions = []
}

export default {
  QUESTIONLIST_UPDATED,
  SET_CURRENTQUESTION,
  UNSET_CURRENTQUESTION,
  RESET_QUESTIONS
}
