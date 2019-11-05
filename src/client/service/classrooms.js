export async function fetchClasses() {
  const _api = window._vm.$http;
  const api_url = `http://localhost:5001/api/v1/school_class/owned`;
  const result = await _api.get(api_url);
  return result;
}

export async function addNewClass(payload) {
  const _api = window._vm.$http;
  const api_url = `http://localhost:5001/api/v1/school_class`;
  const result = await _api.post(api_url, payload);
  return result;
}

export async function fetchCurrentClass(class_id) {
  const _api = window._vm.$http;
  const api_url = `http://localhost:5001/api/v1/school_class/${class_id}`;
  const result = await _api.get(api_url);
  return result;
}

export async function fetchQuizPDF(quiz_id) {
  const _api = window._vm.$http;
  const api_url = `http://localhost:5001/api/v1/class_quiz/pdf_view/${quiz_id}`;
  const result = await _api.get(api_url, { responseType: "blob" });
  return result;
}
