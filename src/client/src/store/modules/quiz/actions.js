import { submitQuiz } from "@/service/quiz_service";

export default {
	SUBMIT_QUIZ({ commit }, payload) {
		submitQuiz(payload).then(result => {
			const { data } = result
		})
		// TODO: commit a success
	}
}
