import Api from "@/service/Api"

export async function fetchQuiz(quiz_id) {
	const result = await Api.get("/class_quiz/" + quiz_id)
	if (result.status == 200) {
		return result.data;
	}
	else {
		return {};
	}
}

export async function submitQuiz(payload) {
	const result = await Api.post("/submit_quiz")
	if (result.status == 200) {
		return result;
	}
	else {
		return {};
	}
}
