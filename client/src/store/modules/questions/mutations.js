const QUESTIONLIST_UPDATED = (state, payload) => {
  state.questions = payload
}

const SET_CURRENTQUESTION = (state, payload) => {
  state.current_question = payload
}

const UNSET_CURRENTQUESTION = (state) => {
  Object.assign(state.current_question, {})
}

export default {
  QUESTIONLIST_UPDATED,
  SET_CURRENTQUESTION,
  UNSET_CURRENTQUESTION
}
