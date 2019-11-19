import Api from "./Api"

export async function fetchClasses() {
	const api_url = "/school_class/owned";
  const result = await Api.get(api_url);
  return result;
}

export async function addNewClass(payload) {
  const api_url = `/school_class`;
  const result = await Api.post(api_url, payload);
  return result;
}

export async function fetchCurrentClass(class_id) {
  const api_url = `/school_class/${class_id}`;
  const result = await Api.get(api_url);
  return result;
}

export async function fetchQuizPDF(quiz_id) {
  const api_url = `/class_quiz/pdf_view/${quiz_id}`;
  const result = await Api.get(api_url, { responseType: "blob" });
  return result;
}
