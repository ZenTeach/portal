export async function fetchQuestions(searchPayload) {
  const _api = window._vm.$http;
  const result = await _api.post(
    "http://localhost:5001/api/v1/question/search",
    searchPayload
  );

  return result;
}
