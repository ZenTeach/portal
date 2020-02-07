export default {
	ADD_TO_SELECTED_QUIZ_QUESTION(state, payload) {
		state.quiz_questions.append(payload)
	},

	REMOVE_SELECTED_QUIZ_QUESTION(state, payload) {
		quiz_id = state.quiz_questions.findIndex(x => x.q_id == payload.q_id)
		state.quiz_questions.slice(quiz_id, 1)
	}
}
