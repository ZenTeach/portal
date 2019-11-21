import Api from "@/service/Api"

export async function fetchQuestions(searchPayload) {
  const result = await Api.post(
    "/question/search",
    searchPayload
  );

  return result;
}
