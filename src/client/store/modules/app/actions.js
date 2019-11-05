import { fetchQuestions } from "../../../service/questions";

export default {
  QUERY_QUESTIONS({ commit }, payload) {
    fetchQuestions(payload).then(result => {
      const {
        data: { data: questions }
      } = result;
      commit("UPDATE_QUESTION_SEARCH", questions);
    });
  }
};
